import streamlit as st
from streamlit_folium import folium_static, st_folium
import folium
import cv2
import numpy as np

import rasterio
from rasterio.warp import transform_bounds
from rasterio.crs import CRS


def overlayFromTIF(image_file):
    dat = rasterio.open(image_file)
    img = dat.read(1)
    print(img.shape)
    print("CRS", dat.crs)
    print("Bounds", dat.bounds)

    img[img[:,:]<0]=0
    bounds = dat.bounds

    xmin, ymin, xmax, ymax = transform_bounds(dat.crs.to_epsg(), 4326, *bounds)

    return img, [[ymax, xmax], [ymin, xmin]]


    
def app():
    # App title
    st.title("Map Centering App")


    '''
    Manage state of the app
    '''
    # Initialize the key in session state
    if 'clicked' not in st.session_state:
        st.session_state.clicked = {1:False}
    
    # Capture feedback from the interaction
    if 'interaction' not in st.session_state:
        st.session_state.interaction = None

    if 'img_dat' not in st.session_state:
        st.session_state.img_dat = None

    if 'bounds' not in st.session_state:
        st.session_state.bounds = None

    # Function to update the value in session state
    def clicked(button, interaction):
        st.session_state.clicked[button] = True
        st.session_state.interaction = interaction

        image_file = r"C:\Users\kenne\OneDrive\Documents\Hackathon Projects\geoai-space-app\data\Map.tif"

        st.session_state.img_dat, st.session_state.bounds = overlayFromTIF(image_file)

    '''
    Input for latitude and longitude coordinates
    '''
    coordinates = st.text_input(
        "Enter comma-separated latitude and longitude (e.g., 48.363352, -80.271750):"
    )

    # Split the input into latitude and longitude
    try:
        lat, lon = map(float, coordinates.split(","))
    except ValueError:
        st.error("Please enter valid latitude and longitude coordinates.")
        st.stop()

     # Create a Leaflet map centered on the entered coordinates
    m = folium.Map(
        tiles="stamenterrain",
        location=[lat, lon],
        zoom_start=18,
        max_zoom=20,
        min_zoom=4,
        scrollWheelZoom=False,
        doubleClickZoom=False,
    )

    folium.Marker(
        location=[lat, lon],
        popup=f"Latitude: {lat}, Longitude: {lon}",
        icon=folium.Icon(color="red", icon="location-pin"),
    ).add_to(m)

    rasterGroup = folium.FeatureGroup(name="Raster")

    if st.session_state.interaction:
        print("Interaction", st.session_state.interaction)
        # lat, lon = interaction['center']['lat'], interaction['center']['lng']
        sw, ne = st.session_state.interaction['bounds']['_southWest'], st.session_state.interaction['bounds']['_northEast']
        center = st.session_state.interaction['center']
        zoom = st.session_state.interaction['zoom']

        swlat, swlon = sw['lat'], sw['lng']
        nelat, nelon = ne['lat'], ne['lng']
        center_lat, center_lon = center['lat'], center['lng']

        st.write(f"Southwest: {swlat}, {swlon}")
        st.write(f"Northeast: {nelat}, {nelon}")
        st.write(f"Center: {center_lat}, {center_lon}")

        # print(img_dat.bounds)
        # print()
        
        rasterGroup.add_child(
            folium.raster_layers.ImageOverlay(
                name="TIF File",
                image=st.session_state.img_dat,
                bounds=st.session_state.bounds,
                opacity=0.6,
                interactive=True,
                cross_origin=False,
                zindex=1,
            )
        )

        # print("Image file", image_file)


    # Display the Leaflet map using folium_static

    interaction = st_folium(
        m,
        width=512,
        height=512,
        zoom=12,
        feature_group_to_add=rasterGroup,
    )

    st.button('Process Coordinates', on_click=clicked, args=[1, interaction])

    
if __name__ == "__main__":
    app()

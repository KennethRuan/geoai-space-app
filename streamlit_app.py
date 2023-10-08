import streamlit as st
from streamlit_folium import folium_static, st_folium
import folium
import numpy as np

import leafmap.foliumap as leafmap

import rasterio
from rasterio.warp import transform_bounds
from rasterio.crs import CRS

from apis import weatherData1, earthquake, events
from datetime import datetime

import json
import geopandas as gpd
import plotly.graph_objs as go

import math

import shapefile

@st.cache_data
def overlayFromTIF(image_file):
    dat = rasterio.open(image_file)
    img = dat.read(1)
    print(img.shape)

    img[img[:,:]<0]=0
    bounds = dat.bounds

    xmin, ymin, xmax, ymax = transform_bounds(dat.crs.to_epsg(), 4326, *bounds)

    return img, [[ymax, xmax], [ymin, xmin]]

def app():
    # App title
    st.title("AI 1000")

    selected = st.sidebar.multiselect(
        'Data to load',
        ['Fire data', 'Flood data', 'Earthquake data']
    ) #use values in selected to determine which maps to render

    st.sidebar.write("---")

    focused = st.sidebar.selectbox(
        'Show detailed data for',
        selected
    )

    # Initialize the key in session state
    if 'clicked' not in st.session_state:
        st.session_state['clicked'] = {1:False}
    
    # Capture feedback from the interaction
    if 'center' not in st.session_state:
        st.session_state['center'] = (48.363352, -80.271750)
    
    if 'zoom' not in st.session_state:
        st.session_state['zoom'] = 10

    if 'eq' not in st.session_state:
        st.session_state['eq'] = []

    # Function to update the value in session state
    def clicked(button, center):
        print("CLICKED")
        st.session_state['clicked'][button] = True
        st.session_state['center'] = center

        st.session_state['eq'] = []
        
        print("RUNNING")
        lat, lon = st.session_state.center
        eqs = earthquake(lat, lon, datetime.now())
        print("EQS", eqs)
        if eqs != None and len(eqs) > 0:
            for eq in eqs:
                print("Adding", eq[2].location, "earthquake with radius", int(math.floor(float(eq[1]["magnitude"]))))
                
                st.session_state['eq'].append(
                    folium.Circle(
                        location=eq[2].location,
                        popup="Earthquake",
                        color="red",
                        fill_color="red",
                        radius=int(math.floor(float(eq[1]["magnitude"])))*500,
                    )
                )
        
        print("FINISHED ADDING EQS, RETURNED", len(eqs if eqs else []))


    tif_display = False
    # if "TIF" in display_layers:
    #     tif_display = True

    # st.write("you selected", display_layers)

    coordinates = st.text_input(
        "Enter comma-separated latitude and longitude (e.g., 48.363352, -80.271750):"
    )

    timestep = st.slider(
        "Time Step",
        0, 9, 0
    )

    base_lat, base_lon = st.session_state.center
    # Split the input into latitude and longitude
    try:
        base_lat, base_lon = map(float, coordinates.split(","))
    except ValueError:
        pass

    m = leafmap.Map(
        google_map="TERRAIN",
        location=[base_lat, base_lon],
        zoom_start=st.session_state['zoom'],
        max_zoom=20,
        min_zoom=4,
    )

    earthquake_layer = folium.FeatureGroup(
        name="Earthquakes"
    )

    for eq in st.session_state['eq']:
        eq.add_to(earthquake_layer)

    eventss = folium.FeatureGroup(
        name="Events"
    )

    # Run all API calls that add geometry to the map

    # evs = events()
    # for ev in evs:
    #     folium.CircleMarker(
    #         location=ev.location,
    #         popup="Event",
    #         color="blue",
    #         fill_color="blue",
    #         radius=5,
    #     ).add_to(eventss)
    # print("ADDED EVENTS", len(evs))
            
    # folium.CircleMarker(
    #     location=[-0.2694, 125.1609],
    #     popup="Earthquake",
    #     color="red",
    #     fill_color="red",
    #     radius=5,
    # ).add_to(earthquake_layer)

    earthquake_layer.add_to(m)

    # img_dat, bounds = overlayFromTIF(r"./data/Map.tif")
    # folium.raster_layers.ImageOverlay(
    #     name="TIF File",
    #     image=img_dat,
    #     bounds=bounds,
    #     opacity=0.6,
    #     interactive=True,
    #     cross_origin=False,
    #     zindex=1,
    #     show=tif_display,
    # ).add_to(m)

    print("HELPPPPP", earthquake_layer.to_dict())

        # print("Image file", image_file)


    folium.LayerControl().add_to(m)


    output = m.to_streamlit(
        bidirectional=True, 
        feature_group_to_add=earthquake_layer
    )

    lat, lon = m.st_map_center(output)

    print(m.st_map_center(output))


    st.button("Process Geometries", on_click=clicked, args=[True, (lat, lon)])

    # shape file 
    # shp_filename = r"C:\Users\kenne\OneDrive\Documents\Hackathon Projects\geoai-space-app\data\nbac_2022_r12_20230630.shp"
    
    # #shp_geojson = shapefile.Reader(shp_filename).__geo_interface__

    # shp_file = gpd.read_file(shp_filename)
    # shp_file.to_file('myJson.geojson', driver='GeoJSON')

    # #m = folium.Map(location=[40, -120], zoom_start=10)
    # st.print("this should be a thing")
    # shp_file.add_to(m)
    # #st.print(shp_geojson)
    # #shp_geojson.add_to(m)

    # Pull data from APIs

    # Call and write weather data
    weather = weatherData1(lat, lon)
    weather_time_label = weather[0][4][timestep]
    weather_data = weather[0][1][timestep]

    # Display statistics
    st.header("Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Lat, Lng: {}, {}".format(lat, lon))

    with col2:
        st.write("**Timestamp:** *" + weather_time_label + "*")
        for i, (k, v) in enumerate(weather_data["details"].items()):
            formattedKey = k.replace("_", " ").title()
            formattedValue = str(v) + " " + str(weather[0][3][i])
            st.write("{}: {}".format(formattedKey, formattedValue))
    
    # Provide feedback based on currently toggled Layers
       
if __name__ == "__main__": 
    app()


    

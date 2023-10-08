import streamlit as st
from streamlit_folium import folium_static, st_folium
import folium
import cv2
import numpy as np
from shapely.geometry import Polygon

image_file = None

# The following two conversion formulas are based on Mercator projections and will not work too close to the poles
def pixelToMeters(latitude, pixel, zoom):
    ground_resolution = (np.cos(np.deg2rad(latitude)) * 40075016.686) / (2**(zoom+8))
    print("Meters per pixel:", ground_resolution)
    return pixel * ground_resolution

# dx and dy are in meters
def displaceLatLon(latitude, longitude, dx, dy, zoom):
    r_earth = 6372798.2
    print("Computing with", latitude, longitude, dx, dy, zoom)

    # Convert dx, dy in pixels at zoom level z to meters
    dx_meters = pixelToMeters(latitude, dx, zoom)
    dy_meters = pixelToMeters(latitude, dy, zoom)

    print(f"dx: {dx_meters}, dy: {dy_meters}")

    new_latitude  = latitude  + (dy_meters / r_earth) * (180 / np.pi)
    new_longitude = longitude + (dx_meters / r_earth) * (180 / np.pi) / np.cos(latitude * np.pi/180)

    return new_latitude, new_longitude


# Function to handle the button click
def process_coordinates(sw, ne, center, zoom, folium_map):
    # You can perform additional processing here
    pass
    


def app():
    global image_file

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

    # Function to update the value in session state
    def clicked(button, interaction):
        st.session_state.clicked[button] = True
        st.session_state.interaction = interaction

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

    '''
    Input for uploading a binary image file
    '''

    image_file = st.file_uploader("Upload a binary image file", type=["jpg", "png", "jpeg"])

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

    polygonGroup = folium.FeatureGroup(name="Polygons")

    # Display the Leaflet map using folium_static

    interaction = st_folium(
        m,
        width=512,
        height=512,
        zoom=12,
    )

    st.button('Process Coordinates', on_click=clicked, args=[1, interaction])


    #Button to trigger processing
    if st.session_state.clicked[1]:
        ss_interaction = st.session_state.interaction

        print("Interaction", ss_interaction)
        # lat, lon = interaction['center']['lat'], interaction['center']['lng']
        sw, ne = ss_interaction['bounds']['_southWest'], interaction['bounds']['_northEast']
        center = ss_interaction['center']
        zoom = ss_interaction['zoom']

        swlat, swlon = sw['lat'], sw['lng']
        nelat, nelon = ne['lat'], ne['lng']
        center_lat, center_lon = center['lat'], center['lng']

        st.write(f"Southwest: {swlat}, {swlon}")
        st.write(f"Northeast: {nelat}, {nelon}")
        st.write(f"Center: {center_lat}, {center_lon}")

        second_map = folium.Map(
            tiles="stamenterrain",
            location=[center_lat, center_lon],
            zoom_start=zoom,
            scrollWheelZoom=False,
            doubleClickZoom=False,
            zoom_control=False,
        )

        print("Image file", image_file)

        # Add the image contours to the map
        if image_file is not None:
            with open(image_file.name,'wb') as f:
                f.write(image_file.read())

            # Read the uploaded image
            image = cv2.imread(image_file.name, 0)
            flipped_image = image[::-1,:]

            # Threshold the image to create a binary mask
            _, binary_image = cv2.threshold(flipped_image, 128, 255, cv2.THRESH_BINARY)

            # Find contours in the binary image
            contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            

            print(f"Found {len(contours)} contours")
            # print(contours)

            # Create polygons from the contours
            polygons = [Polygon(np.squeeze(contour)) for contour in contours]

        
            # Add polygons to the map
            for polygon in polygons:
                pixel_coords = list(polygon.exterior.coords)
                coords = [displaceLatLon(swlat, swlon, point[0], point[1], zoom) for point in pixel_coords]
                # print(coords)
                polygonGroup.add_child(
                    folium.Polygon(
                        locations=coords, 
                        color='red', 
                        fill=True, 
                        fill_color='red', 
                        fill_opacity=0.3
                    )
                )

        st_folium(
            second_map,
            width=512,
            height=512,
            feature_group_to_add=polygonGroup,
        )

    
if __name__ == "__main__":
    app()

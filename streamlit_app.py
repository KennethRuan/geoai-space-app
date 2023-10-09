import streamlit as st
import folium.raster_layers
import folium
import numpy as np

import leafmap.foliumap as leafmap

import rasterio
from rasterio.warp import transform_bounds
from rasterio.crs import CRS

from apis import weatherData1, earthquake_t, events, tsunami
from datetime import datetime

import json
import geopandas as gpd
import plotly.graph_objs as go

import math

import io
from PIL import Image

import zipfile
import os

@st.cache_data
def overlayFromTIF(image_file):
    dat = rasterio.open(image_file)
    img = dat.read(1)
    print(img.shape)
    # print(dat.crs.to_epsg())

    bounds = dat.bounds
    print("Hold up")
    xmin, ymin, xmax, ymax = transform_bounds(9822, 4326, *bounds)
    print("We made it")
    return img, [[ymax, xmax], [ymin, xmin]]

def writeToTXT(data, filename): 
    # Specify the file path
    file_path = r".\files" + filename

    # Open the file in write mode ('w' for write, 'a' for append)
    with open(file_path, 'w') as file:
        # Write the data to the file
        file.write(data)
    # File is automatically closed when the 'with' block exits

    
def generate_download_button(files):
    import zipfile
    zip_file_name = 'data.zip'

    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for file_name in files:
            zipf.write(r".\files" + file_name)
                    
    with open("data.zip", "rb") as file:
        st.download_button(
            label = "Download zipped data",
            data = file,
            file_name = "data.zip",
            mime = 'application/zip'
    )

def app():
    # App title
    st.title("DataBuilder")

    selected = st.sidebar.multiselect(
        'Data to load',
        ['Earthquake data', 'Sea and lake ice data', 'Storm data', 'Tsunami data']
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

    if 'icebergs' not in st.session_state:
        st.session_state['icebergs'] = []

    if 'storms' not in st.session_state:
        st.session_state['storms'] = []

    if 'tsunamis' not in st.session_state:
        st.session_state['tsunamis'] = []

    # Function to update the value in session state
    def clicked(button, center, bounds, el, il, sl, tl):
        print("CLICKED")
        st.session_state['clicked'][button] = True
        st.session_state['bounds'] = bounds
        st.session_state['center'] = center
        
        print("Attempting to save", st.session_state['center'], "to session state")

        st.session_state['eq'] = []

        print("RUNNING")
        # lat, lon = st.session_state.center
        eqs = earthquake_t()
        writeToTXT(json.dumps(eqs), r"\earthquakes.txt")
        print("EQS", eqs)
        if eqs != None and len(eqs) > 0:
            for eq in eqs:
                print("Adding", eq['Latitude'], eq['Longitude'], "earthquake with radius", eq["Magnitude"])
                
                st.session_state['eq'].append(
                    folium.Circle(
                        location=[eq['Latitude'], eq['Longitude']],
                        popup="Earthquake",
                        color="brown",
                        fill_color="brown",
                        radius=int(math.floor(float(eq["Magnitude"])*500)),
                    )
                )
        
        print("FINISHED ADDING EQS, RETURNED", len(eqs if eqs else []))

        if not st.session_state['icebergs'] or not st.session_state['storms']:
            st.session_state['icebergs'] = []
            st.session_state['storms'] = []

            icebergs = []
            storms = []
            
            evs = events()

            for ev in evs:
                if "Iceberg" in ev['popup']:
                    icebergs.append(ev)
                    st.session_state['icebergs'].append(
                        folium.Circle(
                            location=[ev['location'][1], ev['location'][0]],
                            color=ev['color'],
                            popup=ev['popup'],
                            fill_color=ev['fill_color'],
                            opacity=0.6,
                            radius=ev['radius']*1000,
                        )
                    )
                else:
                    storms.append(ev)
                    st.session_state['storms'].append(
                        folium.Circle(
                            location=[ev['location'][1], ev['location'][0]],
                            color=ev['color'],
                            popup=ev['popup'],
                            fill_color=ev['fill_color'],
                            opacity=0.6,
                            radius=ev['radius']*1000,
                        )
                    )
            
            writeToTXT(json.dumps(storms), r"\storms.txt")
            writeToTXT(json.dumps(icebergs), r"\icebergs.txt")
            print("ADDED EVENTS", len(evs))
        
        if not st.session_state['tsunamis']:
            st.session_state['tsunamis'] = []

            tsus = tsunami()
            writeToTXT(json.dumps(tsus), r"\tsunamis.txt")

            for tsu in tsus:
                st.session_state['tsunamis'].append(
                    folium.Circle(
                        location = [tsu['Latitude'], tsu['Longitude']],
                        color = 'blue',
                        popup='Tsunami',
                        fill_color='blue',
                        opacity=0.6,
                        radius=(tsu['Magnitude'])*1000,
                    )
                )

        dummy_map = leafmap.Map(
            google_map="TERRAIN",
            location=center,
            zoom_start=6,
            max_zoom=20,
            min_zoom=4,
        )
        # dummy_map.zoom_to_bounds(bounds)

        el.add_to(dummy_map)
        il.add_to(dummy_map)
        sl.add_to(dummy_map)
        tl.add_to(dummy_map)

        # map to png
        img_data = dummy_map._to_png(5)
        img = Image.open(io.BytesIO(img_data))
        img.save(r'.\files\map-image.png')
        
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

    blat, blon = 0, 0
    # Split the input into latitude and longitude
    try:
        blat, blon = tuple(map(float, coordinates.split(",")))
    except ValueError:
        pass
    if blat == 0 and blon == 0:
        blat, blon = st.session_state['center']

    print("Did it overwrite?", blat, blon)

    m = leafmap.Map(
        google_map="TERRAIN",
        location=[blat, blon],
        zoom_start=6,
        max_zoom=20,
        min_zoom=4,
    )

    # if 'bounds' in st.session_state:
    #     print('bounds', st.session_state['bounds'])
    #     sbounds = st.session_state['bounds']
    #     bounds = [sbounds[0][0], sbounds[0][1], sbounds[1][0], sbounds[1][1]]
    #     m.zoom_to_bounds(st.session_state['bounds'])

    earthquake_layer = folium.FeatureGroup(
        name="Earthquakes",
        show=(True if 'Earthquake data' in selected else False)
    )

    ice_layer = folium.FeatureGroup(
        name="Ice",
        show=(True if 'Sea and lake ice data' in selected else False)
    )

    storm_layer = folium.FeatureGroup(
        name="Storms",
        show=(True if 'Storm data' in selected else False)
    )

    tsunami_layer = folium.FeatureGroup(
        name="Tsunamis",
        show=(True if 'Tsunami data' in selected else False)
    )

    for eq in st.session_state['eq']:
        eq.add_to(earthquake_layer)

    for ev in st.session_state['icebergs']:
        ev.add_to(ice_layer)

    for ev in st.session_state['storms']:
        ev.add_to(storm_layer)

    for tsu in st.session_state['tsunamis']:
        tsu.add_to(tsunami_layer)

    # Run all API calls that add geometry to the map
            
    earthquake_layer.add_to(m)
    ice_layer.add_to(m)
    storm_layer.add_to(m)
    tsunami_layer.add_to(m)


    # Add image layer with data/temperature.png

    # folium.raster_layers.ImageOverlay(
    #     name="Trees",
    #     image=r"./data/can_tree.png",
    #     bounds=[[46.196764, -141.420226], [73.451827, -50.277364]],
    #     opacity=0.6,
    #     interactive=True,
    #     cross_origin=False,
    #     zindex=1,
    #     show=True,
    # ).add_to(m)


    # img_dat, bounds = overlayFromTIF(r".\data\Canada_MFv2020.tiff")
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

    # print("Image file", image_file)


    folium.LayerControl().add_to(m)


    output = m.to_streamlit(
        bidirectional=True,
    )


    # print("Interaction", output)
    center = m.st_map_center(output)
    bounds = m.st_map_bounds(output)
    ubounds = [bounds[0][1], bounds[0][0], bounds[1][1], bounds[1][0]]

    lat, lon = center[0], center[1]

    print("Bounds", ubounds)
    # zoom = output['zoom']

    # swlat, swlon = sw['lat'], sw['lng']
    # nelat, nelon = ne['lat'], ne['lng']
    # center_lat, center_lon = center['lat'], center['lng']

    st.button("Process Data", on_click=clicked, args=[True, center, ubounds, earthquake_layer, ice_layer, storm_layer, tsunami_layer])

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

    # generate download button
    filenames = []
    if "Earthquake data" in selected:
        filenames.append(r"\earthquakes.txt")
    if "Sea and lake ice data" in selected:
        filenames.append(r"\icebergs.txt")
    if "Storm data" in selected:
        filenames.append(r"\storms.txt")
    if "Tsunami data" in selected:
        filenames.append(r"\tsunamis.txt")
    # Check if map-image exists
    if os.path.isfile(r'.\files\map-image.png'):
        filenames.append(r'\map-image.png')
        
    if filenames:
        generate_download_button(filenames)

if __name__ == "__main__": 
    app()


    

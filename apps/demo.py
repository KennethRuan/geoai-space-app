import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd

def process_coordinates(lat, lon):
  # Do something with the coordinates
  st.write(f"Latitude: {lat}, Longitude: {lon}")

def app():
  # App title
  st.title("Map Centering App")

  # Input for latitude and longitude
  coordinates = st.text_input("Enter comma-separated latitude and longitude (e.g., -78.121088, 44.670674):")

  lat, lon = 0, 0
  # Split the input into latitude and longitude
  try:
    lat, lon = map(float, coordinates.split(","))

    print("Got these {}, {}".format(lat, lon))
    m = leafmap.Map(tiles="stamenterrain", lat=lat, lon=lon, zoom=12)
    
    m.to_streamlit()

    if st.button("Process Coordinates"):
      process_coordinates(lat, lon)
		
  except ValueError:
      st.error("Please enter valid latitude and longitude coordinates.")
      st.stop()


  
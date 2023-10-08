import streamlit as st
from streamlit_folium import folium_static, st_folium
import folium
import cv2
import numpy as np

import leafmap.foliumap as leafmap

import rasterio
from rasterio.warp import transform_bounds
from rasterio.crs import CRS

@st.cache_data
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

    col1, col2 = st.columns([5, 1])

    m = folium.Map(
        tiles="stamenterrain",
        location=[43.6532, -79.3832],
        zoom_start=10,
        max_zoom=20,
        min_zoom=4,
    )

    img_dat, bounds = overlayFromTIF(r"./data/Map.tif")
    folium.raster_layers.ImageOverlay(
        name="TIF File",
        image=img_dat,
        bounds=bounds,
        opacity=0.6,
        interactive=True,
        cross_origin=False,
        zindex=1,
    ).add_to(m)

        # print("Image file", image_file)


    folium.LayerControl().add_to(m)

    with col1:
        st_folium(
            m,
            zoom=12,
            height=500
        )

    
if __name__ == "__main__":
    app()

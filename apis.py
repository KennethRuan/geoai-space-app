import geopandas
import matplotlib.pyplot as plt
from cartopy import crs as ccrs
from geodatasets import get_path
import requests
import json
from datetime import datetime 
from datetime import timedelta
import folium

import hashlib

eventToRadius = {
    'Sea and Lake Ice': 4,
    'Wildfires': 10,
    'Volcanoes': 30,
}

def string_to_hex_color(input_string):
    try:
        # Use hashlib to create a hash value from the input string
        hash_object = hashlib.sha256(input_string.encode())
        hex_hash = hash_object.hexdigest()

        # Take the first 6 characters of the hash as the RGB values
        hex_color = "#" + hex_hash[:6]

        return hex_color
    except Exception as e:
        # Handle any exceptions that may occur during the process
        print(f"Error: {e}")
        return None


def weatherData1(lat, lon):
    # api-endpoint for weather data
    URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    
    # defining a parameter dictionary for the parameters to be sent to the API
    params = {
        'lat': str(lat),
        'lon': str(lon)
        #'altitude': 12312
    }

    headers = {
        'User-Agent': "Nasa Space Apps Student Developer Testing"
    }
    
    # sending get request and saving the response as response object
    r = requests.get(url = URL, headers = headers, params = params)
    status= r.status_code

    print("API returned this status: " + str(status))
    # extracting data in json format
    if (status == 200):
        data = r.json()

        # get units and update time
        lastUp = data["properties"]["meta"]["updated_at"]
        measurements = [""] * 7
        i = 0
        for x in data["properties"]["meta"]["units"].values():
            measurements[i] = x
            i = i + 1
        
        timeseries = [{}] * 10
        timemarker = [""] * 10
        i = 0
        for x in range(10):
            j = data["properties"]["timeseries"][x]
            timeseries[i] = j["data"]["instant"]
            timemarker[i] = str(j["time"])
            i = i + 1
        return [("MET Weather Forecast", timeseries, lastUp, measurements, timemarker)]
    else:
        # Return fake generated data for 10 time intervals
        return [("Error Retrieving Forcast Data", [
            {
                "details": {
                    "air_pressure_at_sea_level": 1000,
                    "air_temperature": 10,
                    "cloud_area_fraction": 50,
                    "relative_humidity": 50,
                    "wind_from_direction": 180,
                    "wind_speed": 10
                },
            },
            {
                "details": {
                    "air_pressure_at_sea_level": 1000,
                    "air_temperature": 10,
                    "cloud_area_fraction": 50,
                    "relative_humidity": 50,
                    "wind_from_direction": 180,
                    "wind_speed": 10
                },
            },
            {
                "details": {
                    "air_pressure_at_sea_level": 1000,
                    "air_temperature": 10,
                    "cloud_area_fraction": 50,
                    "relative_humidity": 50,
                    "wind_from_direction": 180,
                    "wind_speed": 10
                },
            },
            {
                "details": {
                    "air_pressure_at_sea_level": 1000,
                    "air_temperature": 10,
                    "cloud_area_fraction": 50,
                    "relative_humidity": 50,
                    "wind_from_direction": 180,
                    "wind_speed": 10
                },
            },
            {
                "details": {
                    "air_pressure_at_sea_level": 1000,
                    "air_temperature": 10,
                    "cloud_area_fraction": 50,
                    "relative_humidity": 50,
                    "wind_from_direction": 180,
                    "wind_speed": 10
                },
            },
            {
                "details": {
                    "air_pressure_at_sea_level": 1000,
                    "air_temperature": 10,
                    "cloud_area_fraction": 50,
                    "relative_humidity": 50,
                    "wind_from_direction": 180,
                    "wind_speed": 10
                },
            },
            {
                "details": {
                    "air_pressure_at_sea_level": 1000,
                    "air_temperature": 10,
                    "cloud_area_fraction": 50,
                    "relative_humidity": 50,
                    "wind_from_direction": 180,
                    "wind_speed": 10
                },
            },
            {
                "details": {
                    "air_pressure_at_sea_level": 1000,
                    "air_temperature": 10,
                    "cloud_area_fraction": 50,
                    "relative_humidity": 50,
                    "wind_from_direction": 180,
                    "wind_speed": 10
                },
            },
            {
                "details": {
                    "air_pressure_at_sea_level": 1000,
                    "air_temperature": 10,
                    "cloud_area_fraction": 50,
                    "relative_humidity": 50,
                    "wind_from_direction": 180,
                    "wind_speed": 10
                }
            }, 
        # Time labels in 1 hour increments ISO format
        ], 0, ["", "", "", "", "", "", ""], [datetime.now().isoformat(), (datetime.now() + timedelta(hours = 1)).isoformat(), (datetime.now() + timedelta(hours = 2)).isoformat(), (datetime.now() + timedelta(hours = 3)).isoformat(), (datetime.now() + timedelta(hours = 4)).isoformat(), (datetime.now() + timedelta(hours = 5)).isoformat(), (datetime.now() + timedelta(hours = 6)).isoformat(), (datetime.now() + timedelta(hours = 7)).isoformat(), (datetime.now() + timedelta(hours = 8)).isoformat(), (datetime.now() + timedelta(hours = 9)).isoformat()])]
    
def events():
    URL = "https://eonet.gsfc.nasa.gov/api/v2.1/events"
    params = {
        'days': 10
    }
    r = requests.get(url = URL, params = params)
    status= r.status_code
    circs = []
    if (status == 200):
        data = r.json()
        for x in (data)["events"]:
            title = x["title"]
            geom = x["geometries"]
            
            type = x["categories"][0]["title"]
            radius = 2

            if (type in eventToRadius.keys()):
                radius = eventToRadius[type]
            
            for loc in geom:
                circ = {
                    'location': loc["coordinates"], 
                    'popup': title, 
                    'fill_color': string_to_hex_color(title), 
                    'radius': radius, 
                    "color": string_to_hex_color(title)
                }
                circs.append(circ)
    return circs

DETECTION_RADIUS = 2000

def earthquake (lat, lon, date):
    req = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson"
    req += "&latitude=" + str(lat)
    req += "&longitude=" + str(lon)
    req += "&maxradiuskm=" + str(DETECTION_RADIUS)
    req += "&endtime=" + str(date) + "&starttime=" + str(date - timedelta(days = 7))

    res = requests.get(req)
    
    if (res.status_code == 200):
        data = json.loads(res.text)
        out = []
        for i in range(data["metadata"]["count"]):
            detailReq = data["features"][i]["properties"]["detail"]
            detailRes = requests.get(detailReq)
            if (not (detailRes.status_code == 200)): continue
            
            detailData = json.loads(detailRes.text)
            prop = detailData["properties"]
            title = prop["title"]
            directory = prop["products"]["origin"][0]["properties"]

            details = {
                "latitude" : directory["latitude"],
                "longitude" : directory["longitude"],
                "magnitude" : directory["magnitude"],
                "depth" : directory["depth"],
                "evaluationStatus" : directory["evaluation-status"],
                "time" : directory["eventtime"]
            }

            geometry = detailData["geometry"]
            geometry = folium.CircleMarker(location=[details["latitude"], details["longitude"]], popup=title, fill_color="#964B00", radius=(details["magnitude"]*5), weight=2, color="#964B00")
            out += [(title, details, geometry)]
        return out
    print("ERROR RETRIEVING EARTHQUAKE DATA", res)
    return []

MAP_KEY = "16133c14a74d297e96d1e954fb77e6e9"
def fireSpots (lat, lon):
    df = 'https://firms.modaps.eosdis.nasa.gov/api/country/csv/' + MAP_KEY + '/MODIS_NRT/CAN/4'
    df_narrow = df[(df['longitude'] >= lon - 10) & (df['latitude'] >= lat - 10) & (df['longitude'] <= lon + 10) & (df['latitude'] <= lat + 10)].copy()

    gdf = geopandas.GeoDataFrame(
        df_narrow, geometry=geopandas.points_from_xy(df_narrow.longitude, df_narrow.latitude), crs="EPSG:4326"
    )

    out = []
    for pin in gdf:
        out += [folium.Marker(location=[pin["latitude"], pin["longitude"]], icon=folium.Icon(color="red"))]
    return out
def tsunami():
    url = "https://ngdc.noaa.gov/hazel//hazard-service/api/v1/tsunamis/events?minYear=2000&minEqMagnitude=6"
    r = requests.get(url)

    if (r.status_code == 200):
        data = r.json()

        # Parse the JSON data
        #data = json.loads(dataa)
    out  = []
    # Extract latitude, longitude, and tsunami magnitude for each item
    for item in data["items"]:
        latitude = item["latitude"]
        longitude = item["longitude"]
        tsunami_magnitude = item.get("tsMtIi", None)  # Some items may not have tsunami magnitude
        if tsunami_magnitude is not None:
            out.append({"Latitude": latitude, "Longitude": longitude, "Magnitude": tsunami_magnitude})
    return out
def earthquake_t():
    url = "https://ngdc.noaa.gov/hazel//hazard-service/api/v1/tsunamis/events?minYear=2000&minEqMagnitude=6"
    r = requests.get(url)
    
    if (r.status_code == 200):
        data = r.json()
    
    out = []
    # Extract latitude, longitude, and tsunami magnitude for each item
    for item in data["items"]:
        latitude = item["latitude"]
        longitude = item["longitude"]
        mag = item["eqMagnitude"]
        out.append({"Latitude": latitude, "Longitude": longitude, "Magnitude": mag})
    return out
    
def vocano():
    url = "https://ngdc.noaa.gov/hazel//hazard-service/api/v1/volcanolocs"
    r = requests.get(url)
    if (r.status_code == 200):
        data = r.json()
    return([(item["latitude"], item["longitude"]) for item in data["items"]])

if __name__ == "main":
    print(earthquake(43.6532, -79.3832, datetime.now()))

  
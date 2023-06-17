import json
import requests
import os
import math
import folium

import streamlit as st
import streamlit_folium as st_folium
import pandas as pd

from geopy.geocoders import Nominatim

from charger_data import color_map

# --------------------------------------------------
# DATA HELPERS
# --------------------------------------------------

'''
Process the charger map data and return a dataframe
'''
def process_data():
    # Read file containing location details
    df = pd.read_json('final.json')

    # If latitude and longitude are not present or empty string, drop the row
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[df["latitude"] != ""]
    df = df[df["longitude"] != ""]

    # Create coords column using lat and lng
    df["coords"] = list(zip(df["latitude"], df["longitude"]))

    return df


# -------------------------------------------------- 
# MAPS HELPERS
# --------------------------------------------------

'''
Take a city name and return the coordinates of the city
'''
def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="reverse_geocoding_example")
    location = geolocator.geocode(city_name, exactly_one=True)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return latitude, longitude
    else:
        return None


'''
Find Euclidean distance between two points
'''
def euclidean_distance(point1, point2):
   return math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(point1, point2)))


'''
Find n closest points to x from list Y
'''
def find_closest_points(x, Y, n):
    distances = []
    for y in Y:
        idx = y[0]
        point = (float(y[1]), float(y[2]))
        distance = euclidean_distance(x, point)
        distances.append((idx, distance))
    
    # Sort based on distance
    distances.sort(key = lambda x : x[1])

    # Get closest points (indices)
    closest_points = [distance[0] for distance in distances]

    return closest_points[:n]


'''
This function takes in the origin and destination coordinates and returns the distance between them.
'''
def find_maps_distance(origin, destination, maps_api_key):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&units=metric&key={maps_api_key}"
    response = requests.get(url).json()
    return response


'''
This function takes in a DataFrame, a given coordinate and returns the details of the
coordinates from the DataFrame nearest to the given coordinate. 
'''
def find_nearest_coordinate(given_coordinate, maps_api_key, n = 5):
    # Get Google Maps API Key
    maps_api_key = os.environ.get("GOOGLE_API_KEY")

    # Create DataFrame by processing the data
    df = process_data()

    # Get closest 20 points (indices) by Euclidean Distance
    closest_points = find_closest_points(given_coordinate, list(zip(list(df.index), list(df['latitude']), list(df['longitude']))), 20)

    # Convert destination coordinate to string
    origin = str(given_coordinate[0]) + ',' + str(given_coordinate[1])

    # Values to be returned
    indices = []
    addresses = []
    distances = []
    durations = []

    # Get distance and duration from origin to each of the closest points using Google Maps API
    for point in closest_points:
        destination = str(df.loc[point]['latitude']) + ',' + str(df.loc[point]['longitude'])
        response = find_maps_distance(origin, destination, maps_api_key)

        address = "".join(response['destination_addresses'])
        distance = response['rows'][0]['elements'][0]['distance']['text']
        duration = response['rows'][0]['elements'][0]['duration']['text']
        
        indices.append(point)
        addresses.append(address)
        distances.append(distance)
        durations.append(duration)

    return indices[:n], distances[:n], durations[:n], addresses[:n]

'''
Take a dataframe and city name as input and display the chargers in that city
'''
def display_city_chargers(city):
    # Create DataFrame by processing the data
    df = process_data()

    # Filter the dataframe to only include chargers in the cities
    df = df[df["city"].isin(city)]

    # If there is only one city, generate a map centered at the city
    if len(city) == 1:
        center_coords = get_coordinates(city)
        zoom_start = 10
    # If there are multiple cities, generate a map centered at India
    else:
        center_coords = (22.845137, 78.672679)
        zoom_start = 5
    map = folium.Map(location=center_coords, zoom_start=zoom_start)

    # Visualize the chargers on the map
    for i, row in df.iterrows():
        color = color_map[row.charger_type]

        coords_x, coords_y = df.loc[i, "coords"]
        if coords_x:
            coords_x = round(float(coords_x), 4)
        if coords_y:
            coords_y = round(float(coords_y), 4)
            folium.Marker(location=df.loc[i, "coords"], icon=folium.Icon(color=color)).add_to(
                map
            )

    # Render Folium map in Streamlit
    return st_folium.st_folium(map, width=725)

def display_chargers_by_location(location):
    # Get Google Maps API Key
    maps_api_key = os.environ.get("GOOGLE_API_KEY")

    # Create DataFrame by processing the data
    df = process_data()
    
    # Get coordinates of the location
    given_coordinate = get_coordinates(location)

    # Get nearest chargers
    indices, distances, durations, addresses = find_nearest_coordinate(
        given_coordinate, maps_api_key, 
    )

    display_chargers_df = []

    # Display chargers
    map = folium.Map(location=given_coordinate, zoom_start=10)
    for idx, distance, duration, address in zip(indices, distances, durations, addresses):
        color = color_map[df.loc[idx, "charger_type"]]

        coords_x, coords_y = df.loc[idx, "coords"]
        if coords_x:
            coords_x = round(float(coords_x), 4)
        if coords_y:
            coords_y = round(float(coords_y), 4)
            folium.Marker(location=df.loc[idx, "coords"], icon=folium.Icon(color=color)).add_to(
                map
            )
        
        # Add values to display_chargers_df
        display_chargers_df.append({
            "Distance": distance,
            "Duration": duration,
            "Address": address,
            "Charger Type": df.loc[idx]["charger_type"]
        })
        
    st_folium.st_folium(map, width=725)
    st.dataframe(pd.DataFrame(display_chargers_df))
    
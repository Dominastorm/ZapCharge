import json
import requests
import os
import math
import folium

import streamlit as st
import streamlit_folium as st_folium
import pandas as pd
import numpy as np


from haversine import haversine
from geopy.geocoders import Nominatim
from sklearn.cluster import DBSCAN

from charger_data import color_map

# --------------------------------------------------
# DATA HELPERS
# --------------------------------------------------

'''
Process the charger map data and return a dataframe
'''
def process_data():
    # Read file containing location details
    df = pd.read_json('charger_map_data.json')

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
            folium.Marker(location=df.loc[i, "coords"],
                          icon=folium.Icon(color=color),
                          tooltip=df.loc[i, "charger_type"],
                          popup=df.loc[i, "address"]).add_to(
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
    i = 0
    for idx, distance, duration, address in zip(indices, distances, durations, addresses):
        color = color_map[df.loc[idx, "charger_type"]]

        # Create Popups
        invisible_character = "⠀"
        popup_distance = invisible_character.join(distance.split(" "))
        popup_duration = invisible_character.join(duration.split(" "))

        coords_x, coords_y = df.loc[idx, "coords"]
        if coords_x:
            coords_x = round(float(coords_x), 4)
        if coords_y:
            coords_y = round(float(coords_y), 4)
            folium.Marker(location=df.loc[idx, "coords"],
                          icon=folium.Icon(color=color),
                          tooltip=df.loc[idx, "charger_type"],
                          popup=f"{i}\n{popup_distance}\n{popup_duration}").add_to(map)
        i += 1

        # Add entered location to map in white color
        folium.Marker(location=given_coordinate,
                      icon=folium.Icon(color="red"),
                      tooltip="Entered Location",
                      popup=location
                     ).add_to(map)

        
        # Add values to display_chargers_df
        display_chargers_df.append({
            "Distance": distance,
            "Duration": duration,
            "Address": address,
            "Charger Type": df.loc[idx]["charger_type"]
        })
        
    st_folium.st_folium(map, width=725)
    st.dataframe(pd.DataFrame(display_chargers_df))


'''
Using points and specified radius, forms clusters based on density
'''
def cluster_by_distance(points, radius):
    distances = []
    n = len(points)
    for i in range(n):
        distances.append([])
        for j in range(i + 1, n):
            distances[-1].append(haversine(points[i], points[j])) #unit is km

    # visited = [0]*n
    clusters = []
    for i in range(n):
        clusters.append([])
        count = 0
        for d in distances[i]:
            count += 1
            if d <= radius:
                clusters[-1].append(points[i+count])

    return clusters

def display_user_requested_chargers():
    # Read csv file containing user requested chargers
    df = pd.read_csv("user_requested_chargers.csv")

    city_coords = (12.927643, 77.581590)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightgreen', 'black']
    n = len(colors)

    coordinates = df.values.tolist()

    st.write("###  Locations requested by users ")

    # Create streamlit columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("##### Shown below is a map of user recommended locations that was generated by us for this demonstration.")
        user_requests_map = folium.Map(location=city_coords, zoom_start=12, control_scale = True)
        for latitude, longitude in coordinates:
            folium.Marker(location=(latitude, longitude), icon=folium.Icon()).add_to(user_requests_map)
        st_folium.st_folium(user_requests_map, width=725, key="user_requests_map")
    with col2:
        st.write("##### Here, you can see the values that we generated.")
        st.dataframe(df, width=300, height=725)
    with col3:
        # Add new value
        st.write("##### You can add new values to the table below. This will help us improve our algorithm.")
        new_latitude = st.text_input("Latitude")
        new_longitude = st.text_input("Longitude")
        if st.button("Add"):
            if new_latitude and new_longitude:
                new_row = pd.DataFrame.from_dict({"latitude": [new_latitude], "longitude": [new_longitude]})
                df = pd.concat([df, new_row])
                df.to_csv("user_requested_chargers.csv", index=False)
                st.success("Added new value")
                st.experimental_rerun()
            else:
                st.error("Please enter both latitude and longitude")

    st.write("### Configuring values for the alogorithm")
    st.write("##### The user can change these values according to their needs. We have set the default values to the ones that we found to be the most optimal.")

    # Configuration - Input boxes for radius and min samples
    radius = st.number_input("Radius", min_value=0.1, max_value=10.0, value=0.5, step=0.1)
    min_samples = st.number_input("Minimum Samples", min_value=5, max_value=50, value=15, step=5)


    st.write("### Clusters formed based on distances (Conventional Clustering)")
    st.write("##### Since the earth is curved, Euclidean distance is not the most appropriate. So, we have computed Haversine distance, that takes into account the curvature of the earth to find distances between all the points. Using this we have used a conventional clustering algorithm to form clusters.")

    clusters_1 = [x for x in cluster_by_distance(coordinates.copy(), radius) if len(x) >= min_samples]
    distance_based_clusters_map = folium.Map(location=city_coords, zoom_start=12)
    for i in range(len(clusters_1)):
        cluster = clusters_1[i]
        color = colors[i % n]
        for point in cluster:
            x, y = point[0], point[1]
            folium.Marker(location= (x, y), icon=folium.Icon(color=color)).add_to(distance_based_clusters_map)

    st_folium.st_folium(distance_based_clusters_map, width=725, key="distance_based_clusters_map")

    st.write("### Clusters formed based on densities (DBSCAN Algorithm)")
    st.write("##### As you saw, the results of the conventional clustering algorithm were not that great. To improve on this, we used the DBSCAN algorithm to construct better clusters.")
    st.warning("Note: The grey markers don't belong to any cluster.")

    epsilon = 0.5 / 6371.0
    db = DBSCAN(eps=epsilon, min_samples=min_samples, algorithm='ball_tree', metric='haversine').fit(np.radians(df.to_numpy()))
    labels = db.labels_
    density_based_clusters_map = folium.Map(location=city_coords, zoom_start=12, control_scale = True)
    for i in range(len(labels)):
        if labels[i] == -1:
            color = 'lightgray'
            folium.Marker(location= coordinates[i], icon=folium.Icon(color=color)).add_to(density_based_clusters_map)

        else:
            color = colors[labels[i] % n]
            folium.Marker(location= coordinates[i], icon=folium.Icon(color=color)).add_to(density_based_clusters_map)
    
    st_folium.st_folium(density_based_clusters_map, width=725, key="density_based_clusters_map")


    st.write("### Final Result - Removing points not part of any cluster")
    st.write("##### After removing the points that don't belong to any cluster we obtain this final result. This can be used by EV charger companies to place their chargers in optimal locations.")

    density_based_clusters_map_1 = folium.Map(location=city_coords, zoom_start=12, control_scale = True)
    for i in range(len(labels)):
        if labels[i] == -1:
            continue

        else:
            color = colors[labels[i] % n]
            folium.Marker(location= coordinates[i], icon=folium.Icon(color=color)).add_to(density_based_clusters_map_1)
    
    st_folium.st_folium(density_based_clusters_map_1, width=725, key="density_based_clusters_map")


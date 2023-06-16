import json
import requests
import os
import math

from geopy.geocoders import Nominatim
import pandas as pd

from charger_data import charger_names, correct_states_map

# --------------------------------------------------
# DATA HELPERS
# --------------------------------------------------

'''
Process the charger map data and return a dataframe
'''
def process_data(charger_map_data):
    charger_map_data = json.loads(charger_map_data)

    # Read file containing location details
    df = pd.DataFrame.from_dict(charger_map_data)

    # Charger ID - Charger Type Mapping
    df["charger_type"] = df.apply(lambda row: charger_names[int(row["type"])], axis=1)

    # If latitude and longitude are not present or empty string, drop the row
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[df["latitude"] != ""]
    df = df[df["longitude"] != ""]

    # Create coords column using lat and lng
    df["coords"] = list(zip(df["latitude"], df["longitude"]))

    # Apply the correct_map to the states in df
    df["state"] = df["state"].apply(lambda x: correct_states_map[x] if x in correct_states_map else x)

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
def find_nearest_coordinate(df, given_coordinate, maps_api_key, n = 5):
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

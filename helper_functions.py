import json
import requests
import os
import math

from geopy.geocoders import Nominatim
import pandas as pd

from charger_data import charger_names, correct_states_map

# DATA HELPERS

'''
Process the charger map data and return a dataframe
'''
def process_data(charger_map_data):
    charger_map_data = json.loads(charger_map_data)

    # Read file containing location details
    df = pd.DataFrame.from_dict(charger_map_data)

    # Charger ID - Charger Type Mapping
    df["charger_type"] = df.apply(lambda row: charger_names[int(row["type"])], axis=1)

    # Create coords column using lat and lng
    df["coords"] = list(zip(df["latitude"], df["longitude"]))

    # Apply the correct_map to the states in df
    df["state"] = df["state"].apply(lambda x: correct_states_map[x] if x in correct_states_map else x)

    return df


# MAPS HELPERS

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
    x = [float(i) for i in x.split(', ')]

    distances = []
    for point in Y:
        distance = euclidean_distance(x, point)
        distances.append((distance, point))

    # Sort based on distance
    distances.sort(key = lambda x : x[0])

    # Get closest points
    closest_points = [distance[1] for distance in distances]

    return closest_points[:n]


'''
This function takes in the origin and destination coordinates and returns the distance between them.
'''
def find_maps_distance(origin, destination, maps_api_key):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&units=metric&key={maps_api_key}"
    response = requests.get(url)
    data = response.json()
    distance = data['rows'][0]['elements'][0]['distance']['value'] / 1000
    return response, distance


'''
This function takes in a DataFrame, a given coordinate and returns the details of the
coordinates from the DataFrame nearest to the given coordinate. 
'''
def find_nearest_coordinate(df, given_coordinate, maps_api_key, n = 5):
    # Extract latitude and longitude columns from the DataFrame
    locations = df[['latitude', 'longitude']]

    # Get closest 20 points by Euclidean Distance
    locations = find_closest_points(given_coordinate, list(zip(list(df['latitude']), list(df['longitude']))), 20)

    # Calculate the distances using the Google Maps Distance Matrix API
    distances = []
    response_texts = []
    for index, row in enumerate(locations):
        origin = f"{row[0]},{row[1]}"
        destination = given_coordinate
        
        response, distance = find_maps_distance(origin, destination, maps_api_key)
        
        distances.append((index, distance))
        response_texts.append(response.text)

    distances.sort(key = lambda x : x[1])

    # Find the index of the coordinate with the least distance
    min_distance_indices = [distance[0] for distance in distances[:n]]

    # Return the details and response.text of the nearest coordinate
    nearest_coordinate_details = []
    nearest_coordinate_distances = []
    nearest_coordinate_responses = []
    
    for min_distance_index in min_distance_indices:
        nearest_coordinate_details.append(df.iloc[min_distance_index])
        nearest_coordinate_distances.append(distances[min_distance_index][1])
        nearest_coordinate_responses.append(response_texts[min_distance_index])
    return nearest_coordinate_details, nearest_coordinate_distances, nearest_coordinate_responses

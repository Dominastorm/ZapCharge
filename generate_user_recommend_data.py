import random
import math
import pandas as pd


def generate_coordinates_within_distance(latitude, longitude, distance):
    # Convert distance from meters to kilometers
    distance_km = random.uniform(0, distance) / 1000.0

    # Convert latitude and longitude to radians
    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude)

    # Calculate a random bearing (in radians)
    random_bearing = random.uniform(0, 2 * math.pi)

    # Calculate the maximum angular distance (in radians) for generating coordinates
    max_angular_distance = distance_km / 6371.0

    # Calculate the new latitude
    new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(max_angular_distance) + math.cos(lat_rad) * math.sin(max_angular_distance) * math.cos(random_bearing))

    # Calculate the new longitude
    new_lon_rad = lon_rad + math.atan2(math.sin(random_bearing) * math.sin(max_angular_distance) * math.cos(lat_rad), math.cos(max_angular_distance) - math.sin(lat_rad) * math.sin(new_lat_rad))

    # Convert the new latitude and longitude back to degrees
    new_latitude = math.degrees(new_lat_rad)
    new_longitude = math.degrees(new_lon_rad)

    return new_latitude, new_longitude

def generate_data(L, distance_meters, iterations):
    for given_latitude, given_longitude in L:
        for _ in range(iterations):
            generated_latitude, generated_longitude = generate_coordinates_within_distance(given_latitude, given_longitude, distance_meters)
            print(round(generated_latitude, 5), round(generated_longitude, 5))
        print()

# L = [(12.899958, 77.559067), (13.008374, 77.551286), (13.013726, 77.567577)]
# distance_meters = 100
# iterations = 20

# L = [(12.917518, 77.585544), (12.935933, 77.535310), (12.980297, 77.598708), (12.979391, 77.637687), (12.970343, 77.644653)]
# distance_meters = 500
# iterations = 30

L = [(12.891442, 77.576690), (12.883189, 77.582958), (12.880897, 77.595722), (12.894222, 77.598295)]
distance_meters = 2000
iterations = 50

generate_data(L, distance_meters, iterations)


with open('data_1.txt', 'r') as file:
    L = []
    for line in file:
        if line and line != '\n':
            L.append([float(x) for x in line.strip().split(' ')])

column_names = ['latitude', 'longitude']
df = pd.DataFrame(L, columns=[column_names])
# df.to_csv('data_1.csv', index=False)
df.to_csv('data_1.csv', mode='a', index=False, header=False)
import os
import pandas as pd

from helper_functions import find_nearest_coordinate
from charger_data import charger_map_data

from helper_functions import process_data

# Example usage
maps_api_key = os.environ.get("GOOGLE_API_KEY")

given_coordinate = (12.938655, 77.581057)
df = process_data(charger_map_data)

indices, distances, durations, addresses = find_nearest_coordinate(
    df, given_coordinate, maps_api_key, 
)

for idx, distance, duration, address in zip(indices, distances, durations, addresses):
    print(f"Index: {idx}")
    print(f"Distance: {distance}")
    print(f"Duration: {duration}")
    print(f"Address: {address}")
    print(f"Charger Type: {df.loc[idx]['charger_type']}")
    print()

import os
import pandas as pd

from helper_functions import find_nearest_coordinate

# Example usage
maps_api_key = os.environ.get("GOOGLE_API_KEY")

given_coordinate = '12.938655, 77.581057'
csv_file_path = 'data/bangalore_data.csv'
df = pd.read_csv(csv_file_path)

nearest_coordinate_details, nearest_coordinate_distances, nearest_coordinate_responses = find_nearest_coordinate(
    df, given_coordinate, maps_api_key, 
)

print("Nearest Coordinate:")
print(nearest_coordinate_details)
print("\nDistance (km):", nearest_coordinate_distances)
print("\nResponse Text:")
for nearest_coordinate_response in nearest_coordinate_responses:
    print(nearest_coordinate_response)

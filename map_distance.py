import requests
import pandas as pd

def find_nearest_coordinate(given_coordinate, csv_file_path, api_key):
    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(csv_file_path)

    # Extract latitude and longitude columns from the DataFrame
    locations = df[['latitude', 'longitude']]

    # Calculate the distances using the Google Maps Distance Matrix API
    distances = []
    response_texts = []
    for index, row in locations.iterrows():
        origin = f"{row['latitude']},{row['longitude']}"
        destination = given_coordinate
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&units=metric&key={api_key}"
        response = requests.get(url)
        data = response.json()
        distance = data['rows'][0]['elements'][0]['distance']['value']
        distances.append(distance / 1000)  # Convert meters to kilometers
        response_texts.append(response.text)

    # Find the index of the coordinate with the least distance
    min_distance_index = distances.index(min(distances))

    # Return the details and response.text of the nearest coordinate
    nearest_coordinate = df.iloc[min_distance_index]
    nearest_coordinate_distance = distances[min_distance_index]
    nearest_coordinate_response = response_texts[min_distance_index]
    return nearest_coordinate, nearest_coordinate_distance, nearest_coordinate_response

# Example usage
given_coordinate = '12.938655, 77.581057'
csv_file_path = '/content/bangalore_data.csv'
api_key = 'API-KEY'

nearest_coordinate, nearest_coordinate_distance, nearest_coordinate_response = find_nearest_coordinate(
    given_coordinate, csv_file_path, api_key
)
print("Nearest Coordinate:")
print(nearest_coordinate)
print("\nDistance (km):", nearest_coordinate_distance)
print("\nResponse Text:")
print(nearest_coordinate_response)

import json

from geopy.geocoders import Nominatim
import pandas as pd

from charger_data import charger_names, correct_states_map


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

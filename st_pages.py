import streamlit as st
from charger_data import charger_map_data, color_map, states, cities
import folium
import streamlit_folium as st_folium

from helper_functions import process_data, get_coordinates

def map_view():
    df = process_data(charger_map_data)

    # Choose state
    state_choices = st.multiselect("Choose State", states)

    # Choose city (based on state)
    city = None
    city_choices = []
    if state_choices:
        for state in state_choices:
            city_choices.extend(cities[state])
        city = st.multiselect("Choose City", city_choices)
    else:
        st.write("Choose a state to see the cities")

    if city:
        # Generate a map centered at city
        city_coords = get_coordinates(city)
        map = folium.Map(location=city_coords, zoom_start=15)

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
        st_data = st_folium.st_folium(map, width=725)

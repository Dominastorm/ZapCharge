import streamlit as st

from charger_data import charger_map_data, states, cities
from helper_functions import display_city_chargers, process_data, get_coordinates

def chargers_by_city_view():
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
        display_city_chargers(df, city)

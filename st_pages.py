import streamlit as st

from charger_data import states, cities
from helper_functions import display_chargers_by_location, display_city_chargers, display_user_requested_chargers

def chargers_by_city_view():
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
        display_city_chargers(city)

def chargers_by_location_view():
    # User input to enter the location
    location = st.text_input("Enter your location")

    if location:
        display_chargers_by_location(location)

def user_requested_chargers_view():
    display_user_requested_chargers()

def display_heatmap_info():
    st.title("Traffic Heatmap ")

    sample_map_image1 = "heatmap/Map_images/Original_map_images/Sun_8.png"
    sample_map_image2 = "heatmap/Map_images/Original_map_images/fri_20.png"

    st.write("##### The heatmap below shows the traffic data patterns in each city. The darker the color, the more traffic in that city. ")

    st.header("Bulding the Heatmap")

    st.write("##### Since there was no ready made heatmap or publically available traffic data, we created our own heatmap using Google maps historical data.")

    st.subheader("Google Maps Data")
    col1, col2 = st.columns(2)
    with col1:
        st.image(sample_map_image1, caption="Traffic on a Sunday Morning")
    with col2:
        st.image(sample_map_image2, caption="Traffic on a Friday Evening")

    st.subheader("Road traffic extraction")
    st.write("##### Extracting just the roads from the map was a challenge. We used OpenCV to extract the roads from the map for each time periods on different days. We then used the extracted roads to create a mask for the heatmap.")

    subtracted_image1 = "heatmap/Map_images/Subtracted_images/Sun_8.png"
    subtracted_image2 = "heatmap/Map_images/Subtracted_images/fri_20.png"

    col1, col2 = st.columns(2)
    with col1:
        st.image(subtracted_image1, caption="Roads on Sunday morning")
    with col2:
        st.image(subtracted_image2, caption="Roads on Friday evening")

    st.subheader("Traffic data combination")
    st.write("##### After the extraction of road traffic data for multile time periods for every day of the week, we combined these images to provide us with the data where the traffic in concentrated")
    st.image('heatmap/blended.png', caption="Combined traffic data")

    st.write("##### Now the common areas of heaby traffic are isolated and extracted. We then used this image to create a mask for the heatmap.")
    st.image('heatmap/traffic_data.png', caption="Isolated traffic data")

    st.subheader("Heatmap creation")
    st.write("##### We then used the isolated traffic data to create a heatmap. The darker the color, the more traffic in that city. ")

    col1, col2 = st.columns(2)
    with col1:
        st.image('heatmap/heatmap.png', caption="Heatmap")
    with col2:
        st.image('heatmap/blr_heatmap2.png', caption="Heatmap Imposed on Map")

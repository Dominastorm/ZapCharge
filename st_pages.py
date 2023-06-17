import streamlit as st

from charger_data import states, cities
from helper_functions import display_chargers_by_location, display_city_chargers, display_charger_consumption_data, display_user_requested_chargers

def chargers_by_city_view():
    st.write("## Chargers by City")
    st.write("##### This view lets the user select the states and the cities present in them and displays the EV chargers present in the selected cities. It provides a good understanding of the current state of the EV charging network.") 
    st.warning("###### Choose the states and their respective cities to view the chargers present in them. You can choose multiple states and cities.")

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
        st.success("Hover over the chargers to view charger company and click on them to see the address")
        display_city_chargers(city)

def chargers_by_location_view():
    st.write("## Chargers by Location")
    st.write("##### This view lets ther enter any location in India and displays the 5 closest EV chargers and their details. This can be very helpful when an EV user is running out of charge and needs to find the closest EV charger.")

    # User input to enter the location
    location = st.text_input("Enter your location")

    if location:
        display_chargers_by_location(location)

def user_requested_chargers_view():
    st.write("## User Requested Chargers")
    st.write("##### The best way to figure out where the users want chargers is to ask the users themselves. Once the users recommend chargers, we can perform clustering to get the locations of approporiate charger placements.")
    
    display_user_requested_chargers()

def display_heatmap_info():
    st.write("## Traffic Heatmap ")

    sample_map_image1 = "heatmap/Map_images/Original_map_images/Sun_8.png"
    sample_map_image2 = "heatmap/Map_images/Original_map_images/fri_20.png"

    st.write("##### The heatmap below shows the traffic data patterns in each city. The darker the color, the more traffic in that city. ")
    st.image('heatmap/blr_heatmap2.png', caption="Heatmap Imposed on Map", width=1080)

    st.write("### Bulding the Heatmap - Google Maps API")

    st.write("##### Since there was no ready made heatmap or publically available traffic data, we created our own heatmap using Google Maps historical data.")
    st.write("##### We used the Google Maps API to get the traffic data for different time periods on different days of the week. For example, here, you can observe the difference in traffic on a Sunday morning and the traffic on a Friday evening.")

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
    st.image('heatmap/blended.png', caption="Combined traffic data", width=1080)

    st.write("##### Now the common areas of heaby traffic are isolated and extracted. We then used this image to create a mask for the heatmap.")
    st.image('heatmap/traffic_data.png', caption="Isolated traffic data", width=1080)

    st.subheader("Heatmap creation")
    st.write("##### We then used the isolated traffic data to create a heatmap. The darker the color, the more traffic in that city. ")

    col1, col2 = st.columns(2)
    with col1:
        st.image('heatmap/heatmap.png', caption="Heatmap")
    with col2:
        st.image('heatmap/blr_heatmap2.png', caption="Heatmap Imposed on Map")

def charger_consumption_data_view():
    st.write("## Consumption Data")
    

    display_charger_consumption_data()
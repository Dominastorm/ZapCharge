import streamlit as st
from streamlit_option_menu import option_menu
import screeninfo

from st_pages import chargers_by_city_view, chargers_by_location_view, charger_consumption_data_view, user_requested_chargers_view, display_heatmap_info

page_config = st.set_page_config(
    page_title="ZapCharge",
    layout="wide",
)

st_style = """<style> footer {visibility: hidden;} </style>"""
st.markdown(st_style, unsafe_allow_html=True)

#  Set orientation of menu based on screen size
screen = screeninfo.get_monitors()[0]
if screen.width > screen.height:
    orientation = "horizontal"
else:
    orientation = "vertical"

selected = option_menu(
    menu_title="ZapCharge",
    menu_icon="lightning-charge-fill",
    options=["Chargers by City", "Chargers by Location", "User Requested Chargers", "Traffic Heatmap", "Charger Consumption Data"],
    icons=["ev-station-fill", "pin-map-fill",  "people-fill", "stoplights-fill", "lightning-charge-fill"], # icons from https://icons.getbootstrap.com/
    default_index=0,
    orientation=orientation,
)

if selected == "Chargers by City":
    chargers_by_city_view()
elif selected == "Chargers by Location":
    chargers_by_location_view()
elif selected == "User Requested Chargers":
    user_requested_chargers_view()
elif selected == "Traffic Heatmap":
    display_heatmap_info()
elif selected == "Charger Consumption Data":
    charger_consumption_data_view()

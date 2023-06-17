import streamlit as st

from streamlit_option_menu import option_menu
from tkinter import * 
from tkinter.ttk import *

from st_pages import chargers_by_city_view, chargers_by_location_view, user_requested_chargers_view, display_heatmap_info

page_config = st.set_page_config(
    page_title="Home",
    layout="wide",
)

st_style = """<style> footer {visibility: hidden;} </style>"""
st.markdown(st_style, unsafe_allow_html=True)

root = Tk()
width = root.winfo_screenwidth()
 
if width < 1000:
    orientation = "vertical"
else:
    orientation = "horizontal"

selected = option_menu(
    menu_title="ZapCharge",
    menu_icon="lightning-charge-fill",
    options=["Chargers by City", "Chargers by Location", "User Requested Chargers", "Traffic Heatmap"],
    icons=["ev-station-fill", "pin-map-fill",  "people-fill", "stoplights-fill"], # icons from https://icons.getbootstrap.com/
    default_index=0,
    orientation=orientation
)

if selected == "Chargers by City":
    chargers_by_city_view()
elif selected == "Chargers by Location":
    chargers_by_location_view()
elif selected == "User Requested Chargers":
    user_requested_chargers_view()
elif selected == "Traffic Heatmap":
    display_heatmap_info()

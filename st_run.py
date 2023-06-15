import streamlit as st
from streamlit_option_menu import option_menu

from st_pages import  map_view

page_config = st.set_page_config(
    page_title="Home",
    layout="wide",
)

st.title("ZapCharge")
st_style = """<style> footer {visibility: hidden;} </style>"""
st.markdown(st_style, unsafe_allow_html=True)

selected = option_menu(
    menu_title="Main Menu",
    options=["Map", "Arguments", "Operators", "Results"],
    icons=["folder", "sliders", "wrench", "bar-chart"], # icons from https://icons.getbootstrap.com/
    default_index=0,
    orientation="horizontal",
)

if selected == "Map":
    map_view()

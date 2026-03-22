import streamlit as st
from home_add import main_add
from dashboard import dashboard_page
from chatbot import chatbot_page
from Front import front_page
from home_remove import main_remove
from shopping import shopping_page

PAGE_CONFIG = {"page_title":"Smart Fridge (Hack4SDG)", 
               "layout":"centered", 
               "initial_sidebar_state":"auto"}

st.set_page_config(**PAGE_CONFIG)


pages = {
    'Fridge Setup': front_page,
    "Add Items":main_add,
    "Remove Items":main_remove,
    "Chill Buddy": chatbot_page,
    "Recipe Generator": shopping_page,
    "Dashboard": dashboard_page
}


st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(pages.keys()))

pages[selection]()
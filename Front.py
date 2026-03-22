import streamlit as st
import pandas as pd
import os
import pickle

def front_page():
    # Title of the application
    st.title("Smart Fridge Setup")

    # Input for number of people
    num_people = st.number_input("Number of People in Household:", min_value=1, value=1)

    # Input for allergy restrictions
    allergies = st.text_area("Update Allergy Restrictions (comma separated):", placeholder="e.g., nuts, dairy, gluten")

    # Input for dietary preferences
    preferences = st.text_area("Update Dietary Preferences (comma separated):", placeholder="e.g., vegetarian, vegan, gluten-free")

    df=pd.DataFrame()

    # Save button
    if st.button("Save Settings"):
        # Append new data to the DataFrame
        df = pd.DataFrame({
            "Num People": [num_people],
            "Allergies": [allergies],
            "Preferences": [preferences]
        })
        
        with open('fridge_setup_data.pkl','wb') as f:
            pickle.dump(df,f)
        
        st.success("Settings saved successfully!")
        st.write(f"Number of People: {num_people}")
        st.write(f"Allergy Restrictions: {allergies}")
        st.write(f"Dietary Preferences: {preferences}")

        st.dataframe(df)

    # Additional information or instructions
    st.info("Please make sure to update your settings regularly for the best experience!")
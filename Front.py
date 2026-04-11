import streamlit as st
import pandas as pd
import os
import json

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
        # Build a data preview for the current inputs
        df = pd.DataFrame({
            "Num People": [num_people],
            "Allergies": [allergies],
            "Preferences": [preferences]
        })

        user_memory_path = os.path.join(os.path.dirname(__file__), "utils", "user_memory.json")
        existing_data = {}
        if os.path.exists(user_memory_path):
            with open(user_memory_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)

        updated_data = existing_data.copy()
        updated_data.setdefault("preferences", {})
        updated_data["preferences"]["household_size"] = int(num_people)
        updated_data["preferences"]["dietary_restrictions"] = [item.strip() for item in allergies.split(",") if item.strip()]
        updated_data["preferences"]["dietary_preferences"] = [item.strip() for item in preferences.split(",") if item.strip()]

        with open(user_memory_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, indent=2)

        st.success("Settings saved successfully to user_memory.json!")
        st.write(f"Number of People: {num_people}")
        st.write(f"Allergy Restrictions: {allergies}")
        st.write(f"Dietary Preferences: {preferences}")

        st.dataframe(df)

    # Additional information or instructions
    st.info("Please make sure to update your settings regularly for the best experience!")
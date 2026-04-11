import pickle
import re
import json 
import pandas as pd
from datetime import datetime
from mistralai import Mistral
import streamlit as st
import ast  # For converting string representation of a list into a Python list
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the API keys
api_key = os.getenv("API_KEY")


def shopping_page():
    # Load the dataset from the pickle file
    df = pd.DataFrame()
    with open("database.pkl", "rb") as f:
        df = pickle.load(f)

    # --------------------------------------------------------------------------------------------------------------
    # Checking expiring items only
    # 'For now we set items expiring in two days for alerts'
    def check_items(df):
        expiring_items = []
        fridge_items = []
        alerts = []

        for index, rows in df.iterrows():
            # Check if the item is expiring within the next 2 days
            if (pd.to_datetime(rows["Expiration"]) - datetime.now()).days <= 2:
                expiring_items.append(rows["Item"])
                alerts.append(
                    f"Expiring soon: {rows['Item']} (expires on {rows['Expiration']})"
                )

            # Add all fridge items (expiring or not) to the fridge_items list for later checking
            fridge_items.append(rows["Item"])

        return expiring_items, fridge_items, alerts

    # -----------------------------------------------------------------------------------------------------------------
    # Load user profile data
    def load_user_profile():
        user_memory_path = os.path.join(
            os.path.dirname(__file__), "utils", "user_memory.json"
        )
        try:
            with open(user_memory_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                preferences = data.get("preferences", {})
                num_people = int(preferences.get("household_size", 1) or 1)
                allergies = preferences.get("dietary_restrictions", [])
                if isinstance(allergies, list):
                    allergies = ", ".join(allergies)
                dietary_prefs = preferences.get("dietary_preferences", [])
                if isinstance(dietary_prefs, list):
                    dietary_prefs = ", ".join(dietary_prefs)
                return {
                    "num_people": num_people,
                    "allergies": allergies,
                    "preferences": dietary_prefs,
                }
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return {"num_people": 1, "allergies": "", "preferences": ""}

    # -----------------------------------------------------------------------------------------------------------------
    # Generate a recipe based on items in the fridge
    def generate_recipe(expiring_items, fridge_items, preference):
        client = Mistral(api_key=api_key)

        # Load user profile
        user_profile = load_user_profile()
        num_people = user_profile["num_people"]
        allergies = user_profile["allergies"]
        dietary_prefs = user_profile["preferences"]

        inputs = [
            {
                "role": "user",
                "content": f"""
                Can you suggest a recipe using the following items that are expiring soon and should be prioritized? 
                These are expiring soon: {expiring_items}.
                These are the other items in my fridge: {fridge_items}.
                My household size is {num_people} people.
                My allergies are: {allergies if allergies else "None"}.
                My dietary preferences are: {dietary_prefs if dietary_prefs else "None"}.
                My preference is: {preference}.
                Also specify why this matches the requirements at the end
                """,
            }
        ]

        completion_args = {"temperature": 0.7, "max_tokens": 2048, "top_p": 1}

        tools = []

        response = client.beta.conversations.start(
            inputs=inputs,
            model="mistral-medium-latest",
            instructions="Keep the tone friendly and helpful, and answer the user's question based on the inventory information provided.",
            completion_args=completion_args,
            tools=tools,
        )
        return response.outputs[0].content

    # -----------------------------------------------------------------------------------------------------------------
    # Ask Mistral to return the missing items based on the recipe
    def get_missing_items(recipe, fridge_items):
        client = Mistral(api_key=api_key)

        inputs = [
            {
                "role": "user",
                "content": f"""
                    Based on the following recipe:
                    {recipe}
                    
                    These are the items I already have in my fridge: {fridge_items}.
                    Please return only the ingredients that are missing from my fridge in the form of python list. strictly no other text besides the python list.
                    """,
            }
        ]

        completion_args = {"temperature": 0.7, "max_tokens": 2048, "top_p": 1}

        tools = []

        response = client.beta.conversations.start(
            inputs=inputs,
            model="mistral-medium-latest",
            instructions="Return only a Python list with missing items. Do not include extra text.",
            completion_args=completion_args,
            tools=tools,
        )
        missing_items = response.outputs[0].content

        print(missing_items)

        # Remove Markdown code fences
        cleaned = re.sub(r"^```python\s*|\s*```$", "", missing_items.strip())

        # Now safely evaluate the list
        try:
            return ast.literal_eval(cleaned.strip())
        except (SyntaxError, ValueError):
            return []

        return missing_items_list

    # --------------------------------------------------------------------------------------------------------
    # Filter out items that are already in the fridge from the missing items list
    def filter_missing_items(missing_items, fridge_items):
        filtered_missing_items = [
            item for item in missing_items if item not in fridge_items
        ]
        return filtered_missing_items

    # --------------------------------------------------------------------------------------------------------
    # Create the final shopping list from missing recipe ingredients only
    def create_final_shopping_list(filtered_missing_items):
        return filtered_missing_items

    # --------------------------------------------------------------------------------------------------------
    # Streamlit application setup
    st.title("Smart Fridge Recipe Recommender")

    with st.form(key="Details"):
        pref = st.text_input("Any special preferences?")

        submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            # Step 1: Check for expiring and other items
            expiring_items, fridge_items, alerts = check_items(df)

            # Step 2: Generate a recipe using Mistral
            recipe = generate_recipe(expiring_items, fridge_items, pref)

            st.write("### Recipe Suggested:")
            st.write(recipe)

            # Step 3: Ask Mistral to return the missing items for the recipe
            missing_items_list = get_missing_items(recipe, fridge_items)

            # Step 4: Filter out the items that are already in the fridge
            filtered_missing_items = filter_missing_items(
                missing_items_list, fridge_items
            )

            # Step 5: Final shopping list only contains items not in the fridge
            shopping_list = create_final_shopping_list(filtered_missing_items)

            st.write("### Shopping List:")
            if shopping_list:
                st.write(shopping_list)
            else:
                st.write("No additional items needed!")

    # Button to generate another recipe
    st.button("Generate another recipe")

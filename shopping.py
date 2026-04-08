import pickle
import re
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
    # Checking expiring or low-quantity items
    # 'For now we set items expiring in two days for alerts'
    def check_items(df):
        expiring_items = []
        low_quantity_items = []
        fridge_items = []
        alerts = []

        for index, rows in df.iterrows():
            # Check if the item is expiring within the next 2 days
            if (rows["Expiration"] - datetime.now()).days <= 2:
                expiring_items.append(rows["Item"])
                alerts.append(
                    f"Expiring soon: {rows['Item']} (expires on {rows['Expiration']})"
                )

            elif rows["Quantity"] <= 1:  # Assuming 1 as the low quantity threshold
                low_quantity_items.append(rows["Item"])
                alerts.append(
                    f"Low quantity: {rows['Item']} (only {rows['Quantity']} left)"
                )

            # Add all fridge items (expiring or not) to the fridge_items list for later checking
            fridge_items.append(rows["Item"])

        return expiring_items, low_quantity_items, fridge_items, alerts

    # -----------------------------------------------------------------------------------------------------------------
    # Generate a recipe based on items in the fridge
    def generate_recipe(expiring_items, fridge_items, preference):
        client = Mistral(api_key=api_key)

        inputs = [
            {
                "role": "user",
                "content": f"""
                                Can you suggest a recipe using the following items that are expiring soon and should be prioritized? 
                                These are expiring soon: {expiring_items}.
                                These are the other items in my fridge: {fridge_items}.
                                My preference is: {preference}.
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
    # Combine the missing items with low-quantity items from the fridge
    def create_final_shopping_list(filtered_missing_items, low_quantity_items):
        # Combine missing items from the recipe with low-quantity items from the fridge
        shopping_list = filtered_missing_items + low_quantity_items
        return shopping_list

    # --------------------------------------------------------------------------------------------------------
    # Streamlit application setup
    st.title("Smart Fridge Recipe Recommender")

    with st.form(key="Details"):
        pref = st.text_input("Any special preferences?")

        submit_button = st.form_submit_button(label="Submit")
        
        if submit_button:
            # Checking for expiring, low quantity, and other items
            expiring_items, low_quantity_items, fridge_items, alerts = check_items(df)

            # Generating a recipe using Mistral
            recipe = generate_recipe(expiring_items, fridge_items, pref)

            st.write("### Recipe Suggested:")
            st.write(recipe)

            # Generating a list of missing items for the recipe
            missing_items_list = get_missing_items(recipe, fridge_items)

            # Filtering out the items that are already in the fridge
            filtered_missing_items = filter_missing_items(
                missing_items_list, fridge_items
            )

            # Combining missing items with low-quantity items for the final shopping list
            shopping_list = create_final_shopping_list(
                filtered_missing_items, low_quantity_items
            )

            st.write("### Shopping List:")
            if shopping_list:
                st.write(shopping_list)
            else:
                st.write("No additional items needed!")

    # Button to generate another recipe
    st.button("Generate another recipe")

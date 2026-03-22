import pickle
import pandas as pd
from datetime import datetime
from mistralai.client import Mistral
import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the API keys
api_key = os.getenv("API_KEY")


def chatbot_page():
    def get_inventory():
        # Load the inventory from the database.pkl file
        df = pd.DataFrame()
        with open("database.pkl", "rb") as f:
            df = pickle.load(f)

        # Format the inventory content as a string
        items = ""
        for index, row in df.iterrows():
            items += str(row) + "\n"  # Adding newline for better readability

        return items

    def response(question):
        # Get the current inventory from the fridge
        inventory = get_inventory()

        client = Mistral(api_key=api_key)

        inputs = [
            {
                "role": "user",
                "content": f"you are a smart chatbot and will answer anything about inventory related question that i have in this fridge below is the content of my fridge {inventory} and this is today's date {str(datetime.now())}",
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

    st.title("Chill Buddy")
    with st.form(key="Details"):
        q = st.text_input("Ask any questions?")

        submit_button = st.form_submit_button(label="Submit")
        if submit_button:
            st.write(response(q))

    st.button("Ask another question!")

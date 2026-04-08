# api_key = 'WXsgdUtUEsM76G6vZJ9TotvFwKYZqu0l'

# client = Mistral(api_key=api_key)

# inputs = [
#         {
#             "role": "user",
#             "content": "you are a smart chatbot and will answer anything about inventory related question that i have in this fridge below is the content of my fridge \"+inventory+\" and this is today's date \"+str(datetime.now())"
#         }
#     ]

# completion_args = {
#     "temperature": 0.7,
#     "max_tokens": 2048,
#     "top_p": 1
# }

# tools = []

# response = client.beta.conversations.start(
#     inputs=inputs,
#     model="mistral-medium-latest",
#     instructions="",
#     completion_args=completion_args,
#     tools=tools,
# )

# print(response)



import os
import requests
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {"chat_id": chat_id, "text": "🧊 Chill Buddy is online! Fridge monitoring active."}

response = requests.post(url, json=payload)
print(response.json())
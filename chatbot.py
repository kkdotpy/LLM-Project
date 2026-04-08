import pickle
import pandas as pd
from datetime import datetime
from mistralai import Mistral
import streamlit as st
from datetime import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils'))
from ics import Calendar, Event
from pathlib import Path
from dotenv import load_dotenv
from helpers_tool_calling import TOOLS
import json  
from google_calendar import add_expiring_items_to_calendar, add_event_to_calendar
from memory import UserMemory


## For RAG
from foodkeeper_rag import get_rag

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='ics')


# Load environment variables from the .env file
load_dotenv()

# Access the API keys
api_key = os.getenv("API_KEY")


## Some functions essentials: Getting inventory, fomratting as text, creating calendar events, adding to calendar etc

def get_inventory():
    # Load the inventory from the database.pkl file
    ## Error handling in case file not found

    # Find the database file regardless of where the script runs from
    # Get the directory where THIS FILE (chatbot.py) is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "database.pkl")   ## Added because when running the check_exp_items from another place it was not able to find the database.pkl file, this makes it more robust to find the file as long as it's in the same directory as chatbot.py

    try:
        with open(db_path, "rb") as f:
            df = pickle.load(f)
        return df
    except FileNotFoundError:
        st.error("Inventory database not found.")
        return pd.DataFrame(columns = ['Item', 'Quantity', 'Expiration', 'Category', 'Barcode'])  # Return an empty DataFrame if file is not found

## Instead of text, json format is easier for the agent to parse and understand the inventory status, especially for tool calling decisions
def format_inventory_as_json(df):
    if df.empty:
        return {"error": "Fridge is empty"}
    
    today = datetime.now().date()
    items_list = []
    
    for index, row in df.iterrows():
        exp_date = pd.to_datetime(row['Expiration']).date()
        days_until = (exp_date - today).days
        
        items_list.append({
            "name": row['Item'],
            "quantity": int(row['Quantity']),
            "expiration": str(exp_date),
            "days_until_expiry": days_until,
            "category": row['Category']
        })
    
    return {
        "total_items": len(df),
        "total_quantity": int(df['Quantity'].sum()),
        "items": items_list
    }


def create_calendar_event(item_name, expiration_date, quantity):
    ## Creating a calendar event for expiring item
    ## Using the ics library to create .ics files that can be imported into calendar applications
    ## used when add_to_calendar tool is called by the agent
    cal = Calendar()
    event = Event()
    event.name = f"{item_name} expires today!"
    event.description = f"{quantity} units of {item_name} will expire.\nCheck your fridge inventory!"
    event.begin = expiration_date
    event.end = expiration_date 
    event.make_all_day()
    cal.events.add(event)

    ## Save the calendar event to an .ics file
    filename = f"calendar_event_{item_name}_{datetime.now().strftime('%Y%m%d')}.ics"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(str(cal))
    
    return filename


def add_to_calendar(item_name, expiry_date, quantity):
    '''Add item to Google Calendar using API'''
    try:

        import importlib
        utils_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils')
        if utils_path not in sys.path:
            sys.path.append(utils_path)
        from utils.google_calendar import add_event_to_calendar
        
        summary = f" {item_name} expires today!"
        description = f"{quantity} units of {item_name} will expire.\nCheck your fridge inventory!"
        
        calendar_link = add_event_to_calendar(
            summary=summary,
            start_date=expiry_date,
            description=description
        )
        
        return f" Added {item_name} to your Google Calendar! View it here: {calendar_link}"
        
    except Exception as e:
        # Fallback to .ics file if Google Calendar fails
        print(f"Google Calendar failed, falling back to .ics: {e}")
        filename = create_calendar_event(item_name, expiry_date, quantity)
        return f"Calendar event created as {filename} (import manually to Google Calendar)"
    

#========================================================================================================================
## This is simply a function for updating on the sidebar (so not a tool for agent but just a helper function for the UI)
def check_expiring_items(days=2):
    """Check which items expire in given days and return a summary string
       Within Chill Buddy's sidebar for quick glance of expiring items
    """
    df = get_inventory()
    if df.empty:
        return "Your fridge is empty."
    
    today = datetime.now().date()
    expiring = []
    
    for index, row in df.iterrows():
        try:
            if isinstance(row['Expiration'], str):
                exp_date = datetime.strptime(row['Expiration'], '%Y-%m-%d').date()
            else:
                exp_date = pd.to_datetime(row['Expiration']).date()
            
            days_until = (exp_date - today).days
            
            if 0 <= days_until <= days:
                expiring.append({
                    'name': row['Item'],
                    'quantity': row['Quantity'],
                    'days_left': days_until
                })
        except Exception as e:
            continue
    
    if not expiring:
        return f"No items expiring in the next {days} days."
    
    # Create summary string
    from collections import defaultdict
    summary = defaultdict(list)
    
    for item in expiring:
        summary[item['name']].append(item)
    
    result = f"📋 Items expiring in {days} days:\n\n"
    for item_name, items in summary.items():
        total_quantity = sum(item['quantity'] for item in items)
        days_list = sorted(set(i['days_left'] for i in items))
        days_str = ', '.join(map(str, days_list))
        result += f"+ {int(total_quantity)} x {item_name} (in {days_str} days)\n"
    
    return result
#========================================================================================================================

def check_expiring_items_list(days=2):
    """Returns a list of dictionaries for calendar creation
       Only items set to expire within the given days are included, 
    """
    df = get_inventory()
    if df.empty:
        return []
    
    today = datetime.now().date()
    expiring = []
    
    for index, row in df.iterrows():
        try:
            exp_date = pd.to_datetime(row['Expiration']).date()
            days_until = (exp_date - today).days
            
            if 0 <= days_until <= days:
                expiring.append({
                    'name': row['Item'],
                    'expiry_date': exp_date.strftime('%Y-%m-%d'),
                    'quantity': row['Quantity'],
                    'days_left': days_until
                })
        except:
            continue
    
    return expiring


## sometimes when user asks to add an item to calendar.ics file without providing expiry date, 
## we can search the database for that item and get its expiry date to add to calendar, this function is for that purpose
def get_item_expiry_from_db(item_name):
    """Search database for an item and return its expiration date"""
    df = get_inventory()
    if df.empty:
        return None
    
    # Search for the item (case insensitive)
    mask = df['Item'].str.lower() == item_name.lower()
    if mask.any():
        row = df[mask].iloc[0]
        exp_date = pd.to_datetime(row['Expiration']).date()
        return exp_date.strftime('%Y-%m-%d')
    return None

## This function is for executing the tools called by the agent, it will be called in chatbot.py when the agent decides to use a tool and will execute the corresponding function and return the result back to the agent for final response generation
def execute_tool_call(tool_name, tool_args, user_memory=None):
    ''' Executing tools upon agent's decision'''

    if tool_name == "update_user_memory":
        if user_memory is None:
            return {"status": "error", "message": "User memory not initialized."}
        pref_type = tool_args.get("preference_type")
        value = tool_args.get("value")


        if pref_type == "goals":
            user_memory.add_goal(value)
        elif pref_type in ["dietary_restrictions", "favorite_foods"]:
            current = user_memory.memory["preferences"].get(pref_type, [])
            if value not in current:
                current.append(value)
                user_memory.save()
        else:
            if pref_type == 'household_size':
                value = int(value) 
            user_memory.update_preference(pref_type, value)

        return {
            "status": "success",
            "message": f"Updated {pref_type}: {value}"
        }

        
    if tool_name == "add_to_calendar":
        item_name = tool_args.get("item_name")
        expiry_date = tool_args.get("expiry_date")
        quantity = tool_args.get("quantity", 1)

        # If no expiry date provided, try to find it in database
        ## For instance; User says "Set a reminder for the chicken expiring next week" -> agent calls add_to_calendar with item_name "chicken" and no expiry date, in this case we can search the database for "chicken" and get its expiry date to create the calendar event, 
        if not expiry_date:
            expiry_date = get_item_expiry_from_db(item_name)
            if not expiry_date:
                return {
                    "status": "error",
                    "message": f"Could not find {item_name} in inventory. Please add the item first or provide expiry date.",
                    "item": item_name
                }
        
        # Initialize results
        ics_filename = None
        calendar_link = None
        google_status = "failed"
        
        # .ics file for manual calendar import is done always
        try:
            ics_filename = create_calendar_event(item_name, expiry_date, quantity)
            ics_status = "success"
        except Exception as e:
            ics_status = f"failed: {e}"
        
        # when api is working, google calendar addition also occurs
        try:
            from utils.google_calendar import add_event_to_calendar
            
            summary = f"⚠️ {item_name} expires today!"
            description = f"Quantity: {quantity} units\nCheck your fridge inventory!\n\n.ics file saved as: {ics_filename}"
            
            calendar_link = add_event_to_calendar(
                summary=summary,
                start_date=expiry_date,
                description=description
            )
            google_status = "success"

        except Exception as e:
            google_status = f"failed: {e}"
        
        # Return combined result
        return {
            "status": "success",
            "message": f"{item_name} added to calendar!",
            "item": item_name,
            "expiry_date": expiry_date,
            "quantity": quantity,
            "ics_file": ics_filename,
            "ics_status": ics_status,
            "google_calendar_link": calendar_link,
            "google_status": google_status
        }
    
    elif tool_name == "check_expiring_items":
        ### returns the list of expiring items in the next given days as specified

        items = check_expiring_items_list(days=tool_args.get("days", 2))
        print(items)
        
        if not items:
            return {
                "status": "empty",
                "message": f"No items expiring in the next {tool_args.get('days', 2)} days.",
                "items": []
            }
        
        return {
            "status": "success",
            "days": tool_args.get("days", 2),
            "count": len(items),
            "items": items  ## items is in the format -> [{'name': 'milk', 'expiry_date': '2025-04-15', 'quantity': 2, 'days_left': 2}, ...]
        }
    
    elif tool_name == "sync_to_google_calendar":
        days = tool_args.get("days", 2)
        items = check_expiring_items_list(days=days)

        if not items:
            return {
                "status": "empty",
                "message": f"No items expiring in the next {days} days to sync.",
                "items": []
            }
        
        results = add_expiring_items_to_calendar(items)
        return {
            "status": "success",
            "message": f"Added {len(results)} items to Google Calendar.",
            "items_added": len(results),
            'calendar_links': results
        }
    
    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}


def response(question, user_memory=None):
    ''' Getting the response from the agent with tool calling capability'''

    df = get_inventory()
    inventory_dict = format_inventory_as_json(df)

    memory_text = ""
    if user_memory is not None:
        memory_text = user_memory.get_context_summary()
        if memory_text:
            memory_text = f"\n\nUser Memory:\n{memory_text}"

    # ## Getting context from RAG --> FoodKeeper provides the context
    rag = get_rag()
    foodkeeper_context = rag.get_context(question, 3)

    # ## Testing what RAG return
    # print(f"DEBUG: FoodKeeper context: {foodkeeper_context}")

    client = Mistral(api_key=api_key)
    
    messages = [{
        "role": "system",
        "content": f"""You are Chill Buddy, an **autonomous fridge assistant** that helps users reduce waste, eat well, and stay organized.

        Today's date: {datetime.now().strftime('%Y-%m-%d')}

        **INVENTORY (JSON):**
        {json.dumps(inventory_dict, indent=2)}

        **USER MEMORY (preferences, goals):**
        {memory_text if memory_text else "No memory yet. Learn from user."}

        **USDA FOODKEEPER GUIDELINES (for cooking & storage):**
        {foodkeeper_context if foodkeeper_context else "No USDA data retrieved."}

        You have different tools to check expiring items, add to calendar, sync to Google Calendar, and update user memory. Use them when appropriate. Chain tools for multi‑step requests.

        HOW TO Respond (Follow these rules):
        1. **Think step by step.** Plan the actions you need into steps and decide what to do, which tools to call.
        2. **Use tools when relevant.** If the user asks about expiring items, call `check_expiring_items`. If they want reminders, call `add_to_calendar`. If they mention goals or preferences, call `update_user_memory`. Use `sync_to_google_calendar` to add multiple items at once.
        3. **Use memory proactively.** If the user has goals (e.g., “reduce food waste”) or dietary restrictions, always consider them when suggesting actions or recipes. When used cite USFISS dataset for information.
        4. When USDA FoodKeeper context is relevant and used, Cite those information in your response to user to seperate generic to actual data driven response.
        5. **Be friendly and helpful.** Keep a warm, practical tone.

        Now answer the user's question accordingly."""

    },

    {
            "role": "user",
            "content": question
    }
    ]
     
    print(f"DEBUG: Initial messages: {messages}")

    # Allow multiple rounds of tool calls
    max_rounds = 10  # Prevent infinite loops
    round_count = 0
    
    while round_count < max_rounds:
        round_count += 1
        print(f"Round {round_count} - Calling agent... \n{'='*50}")

        
        # Call the agent
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.7
        )
        
        print(f"Tool calls: {response.choices[0].message.tool_calls} \n{'-'*50}")
        
        
        # Checking if agent wants to use tools
        if response.choices[0].message.tool_calls:
            print(f"response.choices: {response.choices[0].message}")
            messages.append(response.choices[0].message)  ## Add the agent's message (with tool calls) to the messages so that when we call the agent again after executing the tools, it has the full context of what it said and what tools it called, this is important for the agent to decide if it wants to call more tools or generate final response based on the results of the tools it just called.
            
            # Execute each tool call
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                print(f"DEBUG: Executing {tool_name} with args {tool_args}")
                
                result = execute_tool_call(tool_name, tool_args, user_memory)
                result_str = json.dumps(result)
                print(f"DEBUG: Result: {result_str[:200]}...")  # Print first 200 chars
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": result_str,
                    "tool_call_id": tool_call.id
                })
            
            # Continue the loop - agent might need to call more tools.
            continue
        
        else:
            # No more tool calls, return final response
            print(f"No more tool calls. Returning final response.\n{'='*50}")
            return response.choices[0].message.content
    
    return "Task completed after maximum rounds."


def chatbot_page():
    """Main chatbot UI"""
    
     ## if memory not initialized, initialize it
    if 'user_memory' not in st.session_state:
        st.session_state.user_memory = UserMemory()


    st.title("🤖 Chill Buddy")

    st.markdown("""
    I can help you with:
    - 📋 Check what's in your fridge
    - ⚠️ Find items expiring soon
    - 📅 Add expiration reminders to calendar
    - 📅 Set goals, preferences
    
    **Try asking:**
    - "What's expiring in the next 3 days?"
    - "Add expiring items to my calendar"
    - "Show me everything in my fridge"
    - "Set a reminder for the chicken expiring next week"
    """)
    
    st.divider()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    
    user_memory = st.session_state.user_memory
    
    ## Display chat history
    ## Going through the messages in session state and displaying them in the chat interface.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about your fridge..."):  ## IN the chatbox if something is inputted
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):  ## After inputting , it gets displayed in the chat interface as a user message
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = response(prompt, user_memory=user_memory)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Sidebar with expiring items widget
    with st.sidebar:
        st.subheader("<x> Expiring Soon")
        expiring_summary = check_expiring_items(3)
        
        if "No items" in expiring_summary or "empty" in expiring_summary:
            st.success(expiring_summary)
        else:
            st.warning(expiring_summary)

        
        st.divider()

        # User preferences display
        st.subheader("<> Your Preferences")
        prefs = user_memory.memory["preferences"]
        
        if prefs["goals"]:
            st.write("**Goals:**", ", ".join(prefs["goals"]))
        
        if prefs["dietary_restrictions"]:
            st.write("**Dietary:**", ", ".join(prefs["dietary_restrictions"]))
        
        if prefs["favorite_foods"]:
            st.write("**Favorites:**", ", ".join(prefs["favorite_foods"]))
        
        st.write(f"**Household:** {prefs['household_size']} people")
        st.write(f"**Cooking:** {prefs['cooking_skill_level']}")
        
        if st.button("🔄 Reset Preferences"):
            user_memory.memory["preferences"] = {
                "dietary_restrictions": [],
                "favorite_foods": [],
                "cooking_skill_level": "intermediate",
                "household_size": 1,
                "goals": []
            }
            user_memory.save()
            st.rerun()
        
        st.divider()
        
        if st.button("📅 Download All Calendar Events"):
            # Create combined calendar file
            cal = Calendar()
            expiring_all = check_expiring_items_list(2)
            for item in expiring_all:
                event = Event()
                event.name = f"⚠️ {item['name']} expires!"
                event.begin = item['expiry_date']
                event.end = item['expiry_date']
                event.make_all_day()
                cal.events.add(event)
            
            filename = f"all_expiring_items_{datetime.now().strftime('%Y%m%d')}.ics"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(cal))
            with open(filename, 'rb') as f:
                st.download_button(
                    label="Download Calendar File",
                    data=f,
                    file_name=filename,
                    mime="text/calendar"
                )


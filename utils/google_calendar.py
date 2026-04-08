# utils/google_calendar.py
import pickle
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd
from pathlib import Path

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


## Authentication and function to actually get the service object for Google Calendar API
def get_calendar_service():
    """Authenticate and return Google Calendar service"""

    utils_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(utils_dir, "credentials.json")
    token_path = os.path.join(utils_dir, "token.pickle")

    creds = None
    
    # Load existing token (once authenticated, credentials are saved in token.pickle)
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)  ## credentials for Google Calendar API
    
    # For first time authentication or if token is invalid/expired, go through the flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)  ## Credentials.json is the file we get from Google Cloud Console when we set up OAuth 2.0 credentials
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds) ## builds the service object -> required for interacting with Google Calendar API


## Functions to add events to calendar and clear events (for testing purposes)
## These functions will be called by the proactive agent when it identifies expiring items and decides to add them to the calendar

def add_event_to_calendar(summary, start_date, end_date=None, description=""):
    """Add a single event to Google Calendar"""

    service = get_calendar_service()  ## Calendar service object for API calls
    
    if not end_date:
        end_date = start_date  ## This is for the cases where we have a item which expires on a specific date, so we can set the end date same as start date (all day event)
    
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'date': start_date},
        'end': {
            'date': end_date
        },
        'reminders': {     ## To get the reminders some days before the event, because it will be more useful to get a reminder 
                #before the item actually expires, so that user can take action (like consume or remove the item) before it goes bad
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 3 * 24 * 60},  # 3 days before
                {'method': 'popup', 'minutes': 24 * 60},      # 1 day before
            ]
        },
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event.get('htmlLink')

## When we have a bunch of expiring items (in a list ), this can be used to add all at once to the calendar
## Calls the add_event_to_calendar function for each item in the list and returns the results (like calendar links) for each added event
def add_expiring_items_to_calendar(items_list):
    """Add multiple expiring items to Google Calendar"""
    results = []
    for item in items_list:
        summary = f"⚠️ {item['name']} expires today!"
        description = f"Quantity: {item['quantity']} units\nCategory: {item.get('category', 'Unknown')}"
        link = add_event_to_calendar(summary, item['expiry_date'], description=description)
        results.append({
            'item': item['name'],
            'expiry_date': item['expiry_date'],
            'calendar_link': link
        })
    return results  ## for each item, we get the name, expiry date and the link to the calendar event that was created

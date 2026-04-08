"""

Tools in the context of an agent refers to specific functions that agent can call and execute to perform certain tasks.

For instance: add_to_calendar
Description suggests-> The purpose is to add expiring item to calendar
parameters means: what the functions expects as input (item_name, expiry_date, quantity) and from that as well item_name and expiry_date are required parameters while quantity is optional with default value of 1.

Other functions or tools are : check_expiring_items and sync_to_google_calendar with their respective descriptions and parameters.

"""

# Define tools for the agent
TOOLS= [
    {
        "type": "function",
        "function": {
            "name": "add_to_calendar",
            "description": "Add an expiring food item to calendar as a reminder",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "The name of the food item"
                    },
                    "expiry_date": {
                        "type": "string",
                        "description": "The expiration date in YYYY-MM-DD format"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "The quantity of the item"
                    }
                },
                "required": ["item_name", "expiry_date"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "check_expiring_items",
            "description": "Check which items in the fridge are expiring soon",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days to check ahead",
                        "default": 2
                    }
                }
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "sync_to_google_calendar",
            "description": "Sync expiring items directly to Google Calendar automatically",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days ahead to check (default 2)",
                        "default": 2
                    }
                }
            }
        }
    },

    {
    "type": "function",
    "function": {
        "name": "update_user_memory",
        "description": "Save user preferences like dietary restrictions, goals, favorite foods, household size, or cooking skill.",
        "parameters": {
            "type": "object",
            "properties": {
                "preference_type": {
                    "type": "string",
                    "enum": ["dietary_restrictions", "favorite_foods", "goals", "household_size", "cooking_skill_level"]
                },
                "value": {
                    "type": "string"
                }
            },
            "required": ["preference_type", "value"]
        }
    }
    }
]


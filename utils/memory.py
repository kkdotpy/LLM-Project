## For agents a memory module can be kept to store history of interactions
## IN this case however, we are keeping a simple memory aligned to a single user session
## The things being remembered are the preferences and context


##within /utils/memory.py
import json
import os
from datetime import datetime, timedelta



class UserMemory:
    '''This is a persistent user memory class keeping track of user preferences and context'''

    def __init__(self, memory_file='user_memory.json'):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.memory_path = os.path.join(self.current_dir, memory_file)
        self.memory = self._load_memory()


    def _load_memory(self):
        '''For first time , create memory else Load
        what  preferences contains:
        - dietary_restrictions: e.g. vegan, gluten-free, etc.
        - favorite_foods: list of user's favorite foods
        - cooking_skill_level: beginner, intermediate, advanced
        - household_size: number of people in the household
        - goals: e.g. reduce waste, eat healthier, save money, etc.
        -interaction_history: list of past interactions with the agent (could be used for RAG or just to give the agent more context about the user)
        '''
        try:
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "preferences":{
                    'dietary_restrictions': [],
                    'favorite_foods': [],
                    'cooking_skill_level': 'beginner',
                    'household_size': 1,
                    'goals': []
                },
                'interaction_history': [],
                'user_context': {}
            }
    
    def save(self):
        '''Save the memory to file'''
        with open(self.memory_path, 'w') as f:
            json.dump(self.memory, f, indent=2)

    def update_preference(self, key, value):
        """Update a user preference"""
        self.memory['preferences'][key] = value
        self.save()

    def add_goal(self, goal):
            """Add a user goal"""
            if goal not in self.memory["preferences"]["goals"]:
                self.memory["preferences"]["goals"].append(goal)
                self.save()

    def add_interaction(self, interaction_type, details):
        '''Logging an interaction with agent and saving it to memory'''
        self.memory['interaction_history'].append({
            'type': interaction_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

        if len(self.memory['interaction_history']) > 50:  # Keep only the last 50 interactions to limit memory size
            self.memory['interaction_history'] = self.memory['interaction_history'][-50:]
        self.save()


    def get_context_summary(self):
        ''' This consolidates the information in the memory into a concise summary that can be provided to the agent as context for decision making.'''

        prefs = self.memory['preferences']
        context = []

        if prefs["goals"]:
            context.append(f"User goals: {', '.join(prefs['goals'])}")
        if prefs["dietary_restrictions"]:
            context.append(f"Dietary restrictions: {', '.join(prefs['dietary_restrictions'])}")
        if prefs["favorite_foods"]:
            context.append(f"Favorite foods: {', '.join(prefs['favorite_foods'])}")
        context.append(f"Household size: {prefs['household_size']}")
        context.append(f"Cooking skill: {prefs['cooking_skill_level']}")
        
        if self.memory["interaction_history"]:
            recent = self.memory["interaction_history"][-3:]
            context.append(f"Recent interactions: {len(recent)} in the past session")
            

        return "\n".join(context) if context else "No user context available yet."


    
        

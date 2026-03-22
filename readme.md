# Smart Fridge Platform

## Overview

This project is a smart fridge platform that helps users track the items inside their fridge. The platform offers two ways to manage inventory:  
1. **Selecting items** when added or removed from the fridge.  
2. **Barcode scanning** to quickly track items.  

Additionally, the data collected is utilized to 3 applications:  
- **Chatbot:** Ask questions about your fridge's inventory and receive instant answers.  
- **Shopping List Generator:** Recommends recipes and generates a shopping list for items you don't have yet.
- **Data Visualization Dashboard:** Shows 4 main visualizations to give users an idea what they have in their fridge

## Features

### Inventory Management
- **Add/Remove Items:**
  - Track fridge contents by selecting items or scanning barcodes.
  - Each item are categorized (e.g., fruit, vegetable).
  
- **Data Visualization:**
  - A dashboard is available to provide insights into the fridge's contents, using charts and other visual representations.

### AI-Powered Features
- **Chatbot:** 
  - Ask the chatbot about what’s inside the fridge, expiration dates, or what to cook with the available ingredients.
  
- **Smart Recipe Generator:**
  - Recommends recipes based on available ingredients.
  - Automatically generates a shopping list for missing ingredients.

## Installation

### Prerequisites
- Python 3.7 or later
- Required libraries (you can install them via pip):
  ```bash
  pip install -r requirements.txt

## Setup
- Clone the repository
```bash
git clone https://github.com/christopher540/smart-fridge-hack4sdg-2024-final.git
```
- Navigate to the project directory:
```bash
cd smart-fridge-hack4sdg-2024-final
```
- Make a .env file with the content
```bash
API_KEY= 'Your API Key'
```
- Run the main application:
```bash
streamlit run main.py
```





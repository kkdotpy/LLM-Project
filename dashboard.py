import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
from datetime import datetime

def dashboard_page():
    st.title('Fridge Inventory Dashboard')
    # Create Streamlit columns for a 2x2 grid
    col1, col2 = st.columns(2)
    st.divider()
    col3, col4 = st.columns(2)

    # Function to generate a plot and return the figure with larger size
    def create_large_plot(x, y, title, color):
        fig, ax = plt.subplots(figsize=(6, 6))  # Adjusting the size to make the plot bigger
        ax.plot(x, y, color)
        ax.set_title(title)
        return fig

    df=pd.DataFrame
    with open('database.pkl','rb') as f:
        df=pickle.load(f)

    # First plot in the first column
    with col1:
        fig1,ax1=plt.subplots(figsize=(6,6))
        temp=df.groupby('Category')['Quantity'].sum()
        label=temp.index
        ax1.pie(temp.values,autopct='%1.1f%%',labels=label)
        ax1.set_title('Food Category Distribution')
        st.pyplot(fig1)

    # Second plot in the second column
    with col2:
        fig2,ax2=plt.subplots(figsize=(6,6))
        # Lists to hold items and quantities
        item_exp = []
        quant = []
        colors = []  # List to hold colors based on urgency

        # Iterate through DataFrame to find items expiring in 3 days or less
        for index, rows in df.iterrows():
            days_until_expiration = (rows['Expiration'] - datetime.now()).days
            if days_until_expiration <= 3:
                item_exp.append(rows['Item'])
                quant.append(rows['Quantity'])
                # Assign color based on urgency
                if days_until_expiration == 1:
                    colors.append('red')  # Expired
                elif days_until_expiration == 2:
                    colors.append('orange')  # Expiring today
                elif days_until_expiration == 3:
                    colors.append('yellow')  # Expiring in 2 days

        # Create the bar chart with specified colors
        bars = ax2.bar(item_exp, quant, color=colors)
        ax2.set_title('Food Expiring in 3 Days')

        # Add a color legend
        ax2.legend(handles=[
            plt.Rectangle((0, 0), 1, 1, color='red'), 
            plt.Rectangle((0, 0), 1, 1, color='orange'), 
            plt.Rectangle((0, 0), 1, 1, color='yellow'), 
        ], labels=['Expiring Today', 'Expiring in 2 Days', 'Expiring in 3 Days'])

        # Show the plot in Streamlit
        st.pyplot(fig2)


    # Third plot in the first column of the second row
    with col3:
        fig3, ax3 = plt.subplots(figsize=(6, 6))
        
        # Sort the dataframe by 'Quantity' and select the top 7 items
        top_items = df.nlargest(7, 'Quantity').reset_index()
        top_items=top_items[['Item','Quantity']]
        ax3.barh(top_items['Item'], top_items['Quantity'], color='skyblue')
        ax3.set_xlabel('Quantity')
        ax3.set_title('Top 7 Items by Quantity')

        st.pyplot(fig3)


    # Fourth plot in the second column of the second row
    with col4:
        fig4, ax4 = plt.subplots(figsize=(6, 6))

        exp=[]
        for index,rows in df.iterrows():
            exp.append((rows['Expiration'] - datetime.now()).days)
        
        ax4.set_title('Distribution of Days to Expiration')
        ax4.hist(exp,bins=10)
        st.pyplot(fig4)

    st.subheader('Total Inventory')
    st.dataframe(df)
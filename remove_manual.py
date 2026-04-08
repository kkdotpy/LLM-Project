import streamlit as st
import pickle
import pandas as pd
from datetime import datetime

def remove_manual_page():
    st.title("Manual Removal")

    # Loading the database
    try:
        with open('database.pkl', 'rb') as f:
            df = pickle.load(f)
    except FileNotFoundError:
        st.error("No database found. Please add items first.")

        if st.button("← Back"):
            st.session_state.page = "home"
            st.rerun()
        return

    if df.empty:
        st.warning("No items in inventory to remove.")
        if st.button("← Back"):
            st.session_state.page = "home"
            st.rerun()
        return

    # Displaying current inventory
    st.subheader("Current Inventory")
    st.dataframe(df)

    st.divider()

    # Manual removal form
    with st.form("manual_removal_form"):
        st.subheader("Remove Items")
        
        # Get unique item names from database
        item_list = sorted(df['Item'].unique())
        
        item_name = st.selectbox("Select item to remove", item_list)
        
        # Filter to show only selected item's details
        item_df = df[df['Item'] == item_name]
        st.write(f"Available quantity: {int(item_df['Quantity'].sum())}")
        
        quantity_to_remove = st.number_input(
            "Quantity to remove",
            min_value=1,
            max_value=int(item_df['Quantity'].sum()),
            step=1,
            value=1
        )
        
        remove_method = st.radio(
            "Removal method:",
            ["Remove oldest first (FIFO)", "Remove newest first (LIFO)", "Remove specific expiry date"]
        )
        
        specific_date = None
        if remove_method == "Remove specific expiry date":
            # Get unique expiry dates for this item
            expiry_dates = sorted(item_df['Expiration'].unique())
            specific_date = st.selectbox("Select expiry date to remove from", expiry_dates)
        
        submitted = st.form_submit_button("Remove Items")
        
        if submitted:
            remaining_to_remove = quantity_to_remove
            
            if remove_method == "Remove oldest first (FIFO)":
                # Sort by expiration date (oldest first)
                sorted_df = df[df['Item'] == item_name].sort_values('Expiration')
                
            elif remove_method == "Remove newest first (LIFO)":
                # Sort by expiration date (newest first)
                sorted_df = df[df['Item'] == item_name].sort_values('Expiration', ascending=False)
                
            else:  # Remove specific expiry date
                sorted_df = df[(df['Item'] == item_name) & (df['Expiration'] == specific_date)]
            
            indices_to_process = sorted_df.index.tolist()
            
            for idx in indices_to_process:
                if remaining_to_remove <= 0:
                    break
                    
                current_qty = df.loc[idx, 'Quantity']
                
                if current_qty <= remaining_to_remove:
                    remaining_to_remove -= current_qty    # Remove entire row
                    df = df.drop(idx)
                else:
                    df.loc[idx, 'Quantity'] -= remaining_to_remove  # Reduce quantity
                    remaining_to_remove = 0
            
            if remaining_to_remove > 0:
                st.warning(f"Could only remove {quantity_to_remove - remaining_to_remove} units. {remaining_to_remove} units not found.")
            else:
                st.success(f"Removed {quantity_to_remove} x {item_name}")
            
            with open('database.pkl', 'wb') as f:
                pickle.dump(df, f)
            
            st.rerun()

    st.divider()

    # Quickly remove all of an item
    with st.expander("<o> Remove all of an item"):
        item_to_remove_all = st.selectbox("Select item to remove completely", item_list, key="remove_all")
        if st.button(f"Remove ALL {item_to_remove_all}"):
            df = df[df['Item'] != item_to_remove_all]
            with open('database.pkl', 'wb') as f:
                pickle.dump(df, f)
            st.success(f"Removed all {item_to_remove_all} from inventory")
            st.rerun()

    # Back button
    if st.button("← Back"):
        st.session_state.page = "home"
        st.rerun()
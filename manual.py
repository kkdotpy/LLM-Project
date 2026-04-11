import streamlit as st
import pickle
import pandas as pd
from datetime import datetime
from datetime import datetime, time, date

def manual_page():
    st.title("Manual Entry")

    # Loading existing database
    try:
        with open('database.pkl', 'rb') as f:
            df = pickle.load(f)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Item', 'Quantity', 'Expiration', 'Category', 'Barcode'])

    with st.form("manual_form"):
        item_name = st.text_input("Item name")
        quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
        expiration_date = st.date_input("Expiration date", value=datetime.now())
        category = st.text_input("Category (optional)", value="General")
        submitted = st.form_submit_button("Add to inventory")

        if submitted:
            if not item_name.strip():
                st.error("Please enter an item name")
            else:
                expiration_date = datetime.combine(expiration_date, time.min)
                new_row = pd.DataFrame([[
                    item_name.strip(),
                    quantity,
                    expiration_date,
                    category.strip() or "General",
                    "" 
                ]], columns=['Item', 'Quantity', 'Expiration', 'Category', 'Barcode'])
                
                df = pd.concat([df, new_row], ignore_index=True)
                
                with open('database.pkl', 'wb') as f:
                    pickle.dump(df, f)
                
                st.success(f"Added {quantity} x {item_name} (expires {expiration_date})")
                st.rerun() 

    st.divider()
    st.subheader("Recently added items")
    try:
        with open('database.pkl', 'rb') as f:
            df = pickle.load(f)
        if len(df) > 0:
            st.dataframe(df.tail(5))
        else:
            st.info("No items yet")
    except:
        pass

    if st.button("← Back"):
        st.session_state.page = "home"
        st.rerun()
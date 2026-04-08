import streamlit as st
from PIL import Image
import pickle
import pandas as pd
from datetime import datetime, timedelta
import time


def fruit_page():
    st.title("Fruits")

    images = [
        'fruit_image/apple.jpeg',
        'fruit_image/grape.jpeg',
        'fruit_image/lemon.jpeg',
        'fruit_image/orange.jpeg',
        'fruit_image/pear.jpeg',
        'fruit_image/watermelon.jpeg'
    ]

    item_names = ["Apple", "Grape", "Lemon", "Orange", "Pear", "Watermelon"]
    expiration = [1, 1, 1, 2, 3, 3]

    # Initialize DataFrame in session state
    if 'df' not in st.session_state:
        try:
            with open('database.pkl', 'rb') as f:
                st.session_state.df = pickle.load(f)
        except FileNotFoundError:
            st.session_state.df = pd.DataFrame(columns=['Item', 'Quantity', 'Expiration', 'Category', 'Barcode'])
            with open('database.pkl', 'wb') as f:
                pickle.dump(st.session_state.df, f)

    # Use a form to prevent immediate reruns
    with st.form(key='fruit_form'):
        # Display fruits and collect quantities
        cols = st.columns(3)
        quantities = []  # Local variable, not session state
        
        for i in range(len(images)):
            with cols[i % 3]:
                img = Image.open(images[i])
                img_resized = img.resize((200, 200))
                st.image(img_resized, use_container_width=True)
                
                # NO 'key' parameter - widget won't persist its value
                qty = st.number_input(
                    label='Quantity',
                    min_value=0,
                    value=0,  # Always starts at 0
                    step=1,
                    key=f'qty_{i}_{st.session_state.get("form_submit_count", 0)}'  # Dynamic key
                )
                quantities.append(qty)
        
        # Submit button inside the form
        submitted = st.form_submit_button(label='Submit')
        
        if submitted:
            # Process the submission
            items_added = False
            for i in range(len(images)):
                if quantities[i] > 0:
                    items_added = True
                    st.write(f"{item_names[i]}: {quantities[i]}")
                    data = [item_names[i], quantities[i], 
                           datetime.now() + timedelta(expiration[i]), 'Fruits', '']
                    new_row = pd.DataFrame([data], columns=['Item', 'Quantity', 'Expiration', 'Category', 'Barcode'])
                    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            
            if items_added:
                # Save to file
                with open('database.pkl', 'wb') as f:
                    pickle.dump(st.session_state.df, f)
                st.success('Items added successfully!')
                
                # Increment counter to create new widget keys next time
                if 'form_submit_count' not in st.session_state:
                    st.session_state.form_submit_count = 0
                st.session_state.form_submit_count += 1
                time.sleep(2)  # Small delay to show the success message
                st.rerun()
            else:
                st.warning('No items selected!')

    st.divider()

    # Undo button
    st.subheader('Remove last item added')
    if st.button(label='Undo'):
        if len(st.session_state.df) > 0:
            st.session_state.df = st.session_state.df.drop(st.session_state.df.index[-1])
            with open('database.pkl', 'wb') as f:
                pickle.dump(st.session_state.df, f)
            st.success('Last item removed!')

            time.sleep(2)  
            st.rerun()
        else:
            st.warning("No items to undo!")

    st.divider()
    
    # Show last items
    st.subheader('Last 5 Items Added')
    if len(st.session_state.df) > 0:
        st.dataframe(st.session_state.df.tail(5))
    else:
        st.info("No items in database yet")
import streamlit as st
from PIL import Image
import pickle
import pandas as pd
from datetime import datetime, timedelta


def fruit_page():
    # Set the title of the app
    st.title("Fruits")

    # Define the images for the columns
    images = [
    'fruit_image/apple.jpeg',
    'fruit_image/grape.jpeg',
    'fruit_image/lemon.jpeg',
    'fruit_image/orange.jpeg',
    'fruit_image/pear.jpeg',
    'fruit_image/watermelon.jpeg'
    ]

    # Corresponding item names
    item_names = ["Apple", "Grape", "Lemon", "Orange", "Pear", "Watermelon"]
    expiration=[1,1,1,2,3,3]

    # Initialize session state for quantities if it doesn't exist
    if 'quantities' not in st.session_state:
        st.session_state.quantities = [0] * len(images)


    # Desired height for the images
    desired_height = 200

    # Create a 2x3 column layout
    cols = st.columns(3)

    for i in range(6):
        with cols[i % 3]:
            # Open the image using PIL
            img = Image.open(images[i])
            
            # Resize the image
            img_resized = img.resize((200, 200))

            # Display the resized image
            st.image(img_resized, use_column_width=True)
            st.session_state.quantities[i] = st.number_input(
                label='Quantity', 
                key=f'quantity_{i}', 
                min_value=0, 
                value=st.session_state.quantities[i],
                step=1
            )
        
    with open('database.pkl','rb') as f:
        df=pickle.load(f)

    if st.button(label='Submit'):
        st.write("You have selected:")
        for i in range(len(images)):
            if st.session_state.quantities[i] > 0:
                st.write(f"{item_names[i]}: {st.session_state.quantities[i]}")
                data=[item_names[i],st.session_state.quantities[i],datetime.now()+timedelta(expiration[i]),'Fruits','']
                new_row = pd.DataFrame([data], columns=['Item', 'Quantity', 'Expiration', 'Category', 'Barcode'])
                df = pd.concat([df, new_row], ignore_index=True)
        st.session_state.clear()

    st.divider()

    st.subheader('Remove last item added')
    if st.button(label='Undo'):
        df = df.drop(df.index[-1])

    st.divider()
    st.subheader('Last item Added')
    st.dataframe(df)
    with open('database.pkl','wb') as f:
        pickle.dump(df,f)
                    


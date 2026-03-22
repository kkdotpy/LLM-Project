# Import libraries
import cv2
from pyzbar import pyzbar
import streamlit as st
import pandas as pd
import pickle

def barcode_page():
    # Initialize session state variables
    if 'scanned' not in st.session_state:
        st.session_state.scanned = False
    if 'barcode_info_input' not in st.session_state:
        st.session_state.barcode_info_input = ''

    def read_barcodes(frame):
        barcodes = pyzbar.decode(frame)
        barcode_info = ''
        for barcode in barcodes:
            x, y, w, h = barcode.rect
            barcode_info = barcode.data.decode('utf-8')
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, barcode_info, (x + 6, y-6), font, 2.0, (255, 255, 255), 1)
        return (frame, barcode_info)

    def scan():
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        holder = st.empty()
        while ret:
            ret, frame = camera.read()
            frame, barcode_info = read_barcodes(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            holder.image(frame)
            if barcode_info != '':
                break
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
        st.session_state.scanned = True
        st.session_state.barcode_info_input = barcode_info  # Store barcode info in session state
        st.write('Success!')
        camera.release()
        cv2.destroyAllWindows()

    def clear_cache():
        st.session_state.scanned = False
        st.session_state.barcode_info_input = ''

    # Load existing database
    with open('database.pkl', 'rb') as f:
        df = pickle.load(f)

    # Streamlit title
    st.title('Scan Item')

    item = ''
    quantity = ''
    expiration = ''
    category = ''
    barcode_info = ''

    # If not scanned, start the scanning process
    if not st.session_state.scanned:
        scan()

    # After scanning is complete
    if st.session_state.scanned:
        with st.form(key='Details'):
            item = st.text_input('Enter item name')
            quantity = st.text_input('Enter quantity')
            expiration = st.text_input('Enter item expiration (YY-MM-DD)')
            expiration = pd.to_datetime(expiration)
            category = st.text_input('Enter category')
            barcode = st.text_input('Barcode', value=st.session_state.barcode_info_input)  # Use session state

            # Submit button
            submit_button = st.form_submit_button(label='Submit')
            if submit_button:
                # Store user input into DataFrame
                data = [item, int(quantity), expiration, category, st.session_state.barcode_info_input]
                new_row = pd.DataFrame([data], columns=['Item', 'Quantity', 'Expiration', 'Category', 'Barcode'])
                df = pd.concat([df, new_row], ignore_index=True)

                # Save updated DataFrame to file
                with open('database.pkl', 'wb') as f:
                    pickle.dump(df, f)

    # Add more items button to clear session state
    if st.button('Add more items', key='add', on_click=clear_cache):
        del st.session_state.barcode_info_input
        del st.session_state.scanned

    if st.button(label='Undo'):
        with open('database.pkl','rb') as f:
            df=pickle.load(f)
        df = df.drop(df.index[-1])
        # Save updated DataFrame to file
        with open('database.pkl', 'wb') as f:
            pickle.dump(df, f)

    # Display updated DataFrame
    st.subheader('Last item updated')
    st.dataframe(df.tail(1))

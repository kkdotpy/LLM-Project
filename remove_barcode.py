# Import libraries
import cv2
from pyzbar import pyzbar
import streamlit as st
import pandas as pd
import pickle

def remove_barcode_page():
    # Initialize session state variables
    if 'scanned' not in st.session_state:
        st.session_state.scanned = False
    if 'barcode_info' not in st.session_state:
        st.session_state.barcode_info = ''

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
        st.session_state.barcode_info = barcode_info  # Store barcode info in session state
        st.write('Success!')
        camera.release()
        cv2.destroyAllWindows()

    def clear_cache():
        st.session_state.scanned = False
        st.session_state.barcode_info = ''

    # Load existing database
    with open('database.pkl', 'rb') as f:
        df = pickle.load(f)

    # Streamlit title
    st.title('Scan Item to Remove the item')

    # If not scanned, start the scanning process
    if not st.session_state.scanned:
        scan()

    barcode_info = ''
    quantity = 1

    # After scanning is complete
    if st.session_state.scanned:
        with st.form(key='Details'):
            barcode = st.text_input('Barcode', value=st.session_state.barcode_info)
            if df[df['Barcode'] == barcode].empty:
                st.write('There is no such items, please check the barcode')
            else:
                item_name = df.loc[df['Barcode'] == barcode, 'Item'].iloc[0]
                st.write(f'Item name: {item_name}')
                quantity = st.text_input('Enter quantity', value = 1)

                # Submit button
                submit_button = st.form_submit_button(label='Submit')
                if submit_button:
                    # Delete the item
                    val = int(quantity)

                    while val > 0:
                        # Remove the oldest items (Most Recent Expiry date) First
                        oldest_df = df[df['Item'] == item_name]
                        if oldest_df.empty:
                            break
                        oldest_item_idx = df[df['Item'] == item_name]['Expiration'].idxmin()

                        df.loc[oldest_item_idx, 'Quantity'] -= val
                        val = -df.loc[oldest_item_idx, 'Quantity']
                        if val >= 0:
                            df = df.drop(oldest_item_idx)

                    # Save updated DataFrame to file
                    with open('database.pkl', 'wb') as f:
                        pickle.dump(df, f)
        

    
    # Remove more items button to clear session state
    if st.button('Remove more items', key='remove', on_click=clear_cache):
        del st.session_state.barcode_info_input
        del st.session_state.scanned


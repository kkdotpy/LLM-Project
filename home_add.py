import streamlit as st

# Create a function to manage the navigation between pages
def main_add():
    st.title("Add Items")
    

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Add Fruit"):
            st.session_state.page = "Fruit"
    
    with col2:
        if st.button("Add Vegetable"):
            st.session_state.page = "Vegetable"
    
    with col3:
        if st.button("Barcode"):
            st.session_state.page = "Barcode"


    # Check the current page in session state and load that page
    if "page" not in st.session_state:
        st.session_state.page = "home"  # Default to home

    if st.session_state.page == "Fruit":
        from fruit import fruit_page
        fruit_page()
    elif st.session_state.page == "Vegetable":
        from vegetable import vegetable_page
        vegetable_page()
    elif st.session_state.page == "Barcode":
        from barcode import barcode_page
        barcode_page()



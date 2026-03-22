import streamlit as st

# Create a function to manage the navigation between pages
def main_remove():
    st.title("Remove Items")
    

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Remove Fruit"):
            st.session_state.page = "Fruit"
    
    with col2:
        if st.button("Remove Vegetable"):
            st.session_state.page = "Vegetable"
    
    with col3:
        if st.button("Barcode"):
            st.session_state.page = "Barcode"


    # Check the current page in session state and load that page
    if "page" not in st.session_state:
        st.session_state.page = "home"  # Default to home

    if st.session_state.page == "Fruit":
        from remove_fruit import remove_fruit_page
        remove_fruit_page()
    elif st.session_state.page == "Vegetable":
        from remove_vegetable import remove_vegetable_page
        remove_vegetable_page()
    elif st.session_state.page == "Barcode":
        from remove_barcode import remove_barcode_page
        remove_barcode_page()



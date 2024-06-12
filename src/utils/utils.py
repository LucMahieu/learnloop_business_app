import streamlit as st

def render_next_page_button(page_name):
    # Add button style to app
    with open("assets/css/streamlit_button.css") as f:
        streamlit_button_css = f.read()

    st.markdown(f"<style>{streamlit_button_css}</style>", unsafe_allow_html=True)

    # Display button with link to next page
    button_html = f'<a href="/{page_name}" target="_self" class="streamlit-button">Volgende</a>'
    st.markdown(button_html, unsafe_allow_html=True)
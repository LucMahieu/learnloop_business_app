import streamlit as st

st.set_page_config(page_title="Beeckestijn", page_icon="🔵", layout='centered', initial_sidebar_state='auto')

class Overzicht:
    def __init__(self):
        pass

    def write_something(self):
        st.title("Technische demo Beeckestijn")
        st.write("""De technische uitwerking van onderstaande onderdelen van de demo:
                 \n 1. Probleemstelling bepalen
                 \n 2. Case doorlopen
                 \n 3. Feedback op slides""")

    def render_next_page_button(self, page_name):

        # Add button style to app
        with open("assets/css/streamlit_button.css") as f:
            streamlit_button_css = f.read()

        st.markdown(f"<style>{streamlit_button_css}</style>", unsafe_allow_html=True)

        # Display button with link to next page
        button_html = f'<a href="/{page_name}" target="_self" class="streamlit-button">Volgende</a>'
        st.markdown(button_html, unsafe_allow_html=True)

if __name__ == "__main__":
    overzicht = Overzicht()
    overzicht.write_something()
        

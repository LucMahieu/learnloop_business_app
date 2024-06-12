import streamlit as st

class FeedbackOpSlides:
    def __init__(self):
        self.run()

    def run(self):
        st.query_params["phase"] = 3
        st.write("Feedback op slides verwerken")
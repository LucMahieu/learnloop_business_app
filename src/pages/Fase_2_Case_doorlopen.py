import streamlit as st
from utils.utils import render_next_page_button

class CaseDoorlopen:
    def __init__(self):
        pass

    def run(self):
        st.title("Case doorlopen")   
        render_next_page_button("Fase_3_Feedback_op_slides")

if __name__ == "__main__":
    case_doorlopen = CaseDoorlopen()
    case_doorlopen.run()

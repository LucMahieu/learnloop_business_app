import streamlit as st
import json
import os
from utils.openai_client import connect_to_openai

class StakeholderChat:
    def __init__(self, name, probleemstelling, module):
        self.client = connect_to_openai()
        self.initialize_session_state()
        self.name = name
        self.probleemstelling = probleemstelling
        self.module = module

    def initialize_session_state(self):
        """
        Initialize session variables if they don't exist.
        """
        if "openai_model" not in st.session_state:
            st.session_state.openai_model = "gpt-4o"

        if "stakeholder_messages" not in st.session_state:
            st.session_state.stakeholder_messages = []

    def display_chat_messages(self):
        """
        Display chat messages in the Streamlit app.
        """
        for message in st.session_state.stakeholder_messages:
            with st.chat_message(message["role"], avatar='👔' if message["role"] == "assistant" else '🔘'):
                st.markdown(message["content"])

    def add_to_assistant_responses(self, response):
        """
        Add the response message to the chat.
        """
        st.session_state.stakeholder_messages.append({"role": "assistant", "content": response})

    def add_to_user_responses(self, user_input):
        """
        Add the user input to the chat.
        """
        st.session_state.stakeholder_messages.append({"role": "user", "content": user_input})

    def generate_assistant_response(self, user_input):
        """
        Generate a response from the assistant.
        """
        role_prompt = open("./assets/prompts/chat_met_stakeholder.txt").read()
        stream = self.client.chat.completions.create(
            model=st.session_state.openai_model,
            messages=[
                {"role": "system", "content": role_prompt},
                *({"role": m["role"], "content": m["content"]} for m in st.session_state.stakeholder_messages)
            ],
            stream=True,
        )
        
        return stream

    def handle_user_input(self):
        """
        Process user input and generate a response.
        """
        if user_input := st.chat_input("Jouw antwoord"):
            self.add_to_user_responses(user_input)
            with st.chat_message("user", avatar='🔘'):
                st.markdown(f"{user_input}")

            with st.chat_message("assistant", avatar='👔'):
                response = st.write_stream(self.generate_assistant_response(user_input))
                self.add_to_assistant_responses(response)
            
            if response == "Top! Laten we doorgaan naar de volgende fase.":
                with st.chat_message("assistant", avatar='👔'):
                    st.button("Volgende")

    def main(self):
        self.initialize_session_state()

        st.title("Chat met stakeholder")

        if st.session_state.stakeholder_messages == []:
            intro_text = f"Hi, mijn naam is {self.name}. We gaan het hebben over het probleem: {self.probleemstelling} Wat wil je precies van mij weten?"
            self.add_to_assistant_responses(intro_text)

        self.display_chat_messages()
        self.handle_user_input()


if __name__ == "__main__":
    stakeholder_chat = StakeholderChat("Lisa de Vries", "LearnLoop heeft slecht klantcontact.")
    stakeholder_chat.main()
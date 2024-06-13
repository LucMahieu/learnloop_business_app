import streamlit as st
from utils.openai_client import connect_to_openai
from utils.utils import render_next_page_button

class Probleemstelling:
    def __init__(self):
        self.company_name = 'LearnLoop'
        self.course = 'Customer Experience & Journey Management'
        self.client = connect_to_openai()
        self.initialize_session_state()

    def initialize_session_state(self):
        """
        Initialize session variables if they don't exist.
        """
        if "openai_model" not in st.session_state:
            st.session_state.openai_model = "gpt-4o"

        if "messages" not in st.session_state:
            st.session_state.messages = []


    def display_chat_messages(self):
        """
        Display chat messages in the Streamlit app.
        """
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar='🔵' if message["role"] == "assistant" else '🔘'):
                st.markdown(message["content"])

    def add_to_assistant_responses(self, response):
        """
        Add the response message to the chat.
        """
        st.session_state.messages.append({"role": "assistant", "content": response})

    def add_to_user_responses(self, user_input):
        """
        Add the user input to the chat.
        """
        st.session_state.messages.append({"role": "user", "content": user_input})

    def generate_assistant_response(self):
        """
        Generate a response from the assistant.
        """
        role_prompt = open("./assets/prompts/probleemstelling_bepalen.txt").read() + f"\nBedrijf van cursist: {self.company_name}" + f"\nCursus: {self.course}"
        stream = self.client.chat.completions.create(
            model=st.session_state.openai_model,
            messages=[
                {"role": "system", "content": role_prompt},
                *({"role": m["role"], "content": m["content"]} for m in st.session_state.messages)
            ],
            stream=True,
        )
        
        return stream
    
    # def extract_problem_statement(self, response):
    #     """
    #     Extract the problem statement from the response.
    #     """
    #     problem_statement = response.split("\n\n")[1]
    #     return problem_statement
    

    def extract_problem_statement(self, response):
        """
        Generate a response from the assistant.
        """
        role_prompt = open("./assets/prompts/extract_problem_statement.txt").read()
        response = self.client.chat.completions.create(
            model=st.session_state.openai_model,
            messages=[
                {"role": "system", "content": role_prompt},
                {"role": "assistant", "content": response} # Take the third last message from the chat
            ]
        )
        return response.choices[0].message.content


    def handle_user_input(self):
        """
        Process user input and generate a response.
        """
        if user_input := st.chat_input("Jouw antwoord"):
            self.add_to_user_responses(user_input)
            with st.chat_message("user", avatar='🔘'):
                st.markdown(f"{user_input}")

            with st.chat_message("assistant", avatar='🔵'):

                response = st.write_stream(self.generate_assistant_response())
                self.add_to_assistant_responses(response)

                if st.session_state.messages[-1]['content'] == "Top! Laten we doorgaan naar de volgende fase.":
                #     render_next_page_button("Fase_2_Case_doorlopen")

                    # Save the problem statement in the session state
                    st.session_state.problemstatement = self.extract_problem_statement(st.session_state.messages[-3]['content']) # TODO: Bad practice. Need to change it to JSON and make it adaptive instead of hardcoded
                    # st.write(f"Probleemstelling: {st.session_state.problemstatement}")
                    

    def run(self):
        self.initialize_session_state()

        st.title("Probleemstelling bepalen")

        if st.session_state.messages == []:
            intro_text = f"Laten we de probleemstelling formuleren. Hoe zou jij jouw probleemstelling formuleren met betrekking tot {self.course} bij {self.company_name}?"
            self.add_to_assistant_responses(intro_text)

        self.display_chat_messages()
        self.handle_user_input()

if __name__ == "__main__":
    probleemstelling = Probleemstelling()
    probleemstelling.run()

import streamlit as st
from utils.openai_client import connect_to_openai

# Configure the Streamlit page settings
st.set_page_config(page_title="Beeckestijn", page_icon="🔵", layout='centered', initial_sidebar_state='auto')

def initialize_session_state():
    """
    Initialize session variables if they don't exist.
    """
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o"

    if "messages" not in st.session_state:
        st.session_state.messages = []


def display_chat_messages():
    """
    Display chat messages in the Streamlit app.
    """
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar='🔵' if message["role"] == "assistant" else '🔘'):
            st.markdown(message["content"])


def add_to_assistant_responses(response):
    """
    Add the response message to the chat.
    """
    st.session_state.messages.append({"role": "assistant", "content": response})


def add_to_user_responses(user_input):
    """
    Add the user input to the chat.
    """
    st.session_state.messages.append({"role": "user", "content": user_input})


def generate_assistant_response(response):
    """
    Generate a response from the assistant.
    """
    role_prompt = open("./assets/prompts/probleemstelling_bepalen.txt").read() + f"\nBedrijf van cursist: {company_name}" + f"\nCursus: {course}"
    stream = client.chat.completions.create(
        model=st.session_state.openai_model,
        messages=[
            {"role": "system", "content": role_prompt},
            *({"role": m["role"], "content": m["content"]} for m in st.session_state.messages)
        ],
        stream=True,
    )
    
    yield stream
    # return stream


def handle_user_input(client, company_name, course):
    """
    Process user input and generate a response.
    """
    if user_input := st.chat_input("Jouw antwoord"):
        add_to_user_responses(user_input)
        with st.chat_message("user", avatar='🔘'):
            st.markdown(f"{user_input}")

        with st.chat_message("assistant", avatar='🔵'):
            stream = generate_assistant_response(user_input)
            response = st.write_stream(stream)
            add_to_assistant_responses(response)


if __name__ == "__main__":
    client = connect_to_openai()

    initialize_session_state()

    st.title("Probleemstelling bepalen")
    company_name = 'LearnLoop'
    course = 'Customer Experience & Journey Management'

    if st.session_state.messages == []:
        intro_text = f"Laten we de probleemstelling formuleren. Hoe zou jij jouw probleemstelling formuleren met betrekking tot {course} bij {company_name}?"
        add_to_assistant_responses(intro_text)

    display_chat_messages()

    handle_user_input(client, company_name, course)

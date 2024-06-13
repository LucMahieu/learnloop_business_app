import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def connect_to_openai():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY_RV"))
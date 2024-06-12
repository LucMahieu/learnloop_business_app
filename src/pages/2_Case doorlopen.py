import streamlit as st
import json
import os
from utils.openai_client import connect_to_openai

class Case:
    def __init__(self):
        self.client = connect_to_openai()
        self.initialize_session_state()

    def initialize_session_state(self):
        if "page" not in st.session_state:
            st.session_state.page = "home"
        
        if "probleemstelling" not in st.session_state:
            st.session_state.probleemstelling = 'Bij LearnLoop leidt het gebrek aan duidelijke doelstellingen en KPIs voor klanttevredenheid ertoe dat alle teams ad hoc beslissingen nemen bij het oplossen van klantproblemen, zoals retouren en restituties, wat resulteert in inconsistente klantbeleving en verwarring bij klanten over het retourbeleid.'

        if "overview" not in st.session_state:
            st.session_state.overview = None

    def main(self):
        if st.session_state.page == "home":
            self.home_screen()
        elif st.session_state.page == "overview_screen":
            self.overview_screen()
        elif st.session_state.page == "onderzoeksmodules":
            self.onderzoeksmodules()
        
    def home_screen(self):
        st.title("Welkom bij het doorlopen van de case")
        st.write("Dit is het beginscherm. Klik op de knop hieronder om verder te gaan.")
        if st.button("Ga naar overzichtsscherm"):
            st.session_state.page = "overview_screen"
            st.rerun()
    
    def read_prompt(self, prompt_name):
        prompt_path = f'./assets/prompts/{prompt_name}.txt'
        with open(prompt_path, 'r') as f:
            prompt = f.read()
        return prompt
    
    def load_overview(self):
        # Lees de JSON-gegevens uit het bestand
        if os.path.exists('./data/generated_data/bedrijfsoverzicht.json'):
            with open('./data/generated_data/bedrijfsoverzicht.json', 'r') as json_file:
                overview_json = json.load(json_file)
                return overview_json
        else:
            return "Overzicht bestand niet gevonden."

    #TODO: probleemstelling moet gekregen worden uit andere scherm
    def generate_overview(self):
        system_message = self.read_prompt('generate_bedrijfsomschrijving')
        user_message = st.session_state.probleemstelling
        bedrijfsoverzicht_json_response = self.openai_call(system_message, user_message, True)
        return bedrijfsoverzicht_json_response

    def openai_call(self, system_message, user_message, json_response=False):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        print(f"Started generation with prompt: {system_message}")
        response = self.client.chat.completions.create(
            model="gpt-4o",
            temperature=0.2,
            messages=messages
        )
        print(f"Generation succesfull")
        content = response.choices[0].message.content
        if json_response:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                st.error("Fout bij het decoderen van JSON respons.")
                return None
        return content

    #TODO: Als er al een bedrijfsoverzicht gemaakt is, dan zal deze eerst verwijderd moeten worden.
    def overview_screen(self):
        st.title("Overzicht")
        if not os.path.exists('./data/generated_data/bedrijfsoverzicht.json'):
            st.write("Een moment geduld, het overzicht wordt gegenereerd...")
            overview = self.generate_overview()
            if overview:
                st.rerun()
            else:
                st.write("Er is een fout opgetreden bij het genereren van het overzicht.")
        else:
            st.write("Dit is het gegenereerde overzicht:")
            overview = self.load_overview()
            st.write(overview)
        
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Ga terug"):
                st.session_state.page = "home"
                st.rerun()
        with col2:
            if st.button("Ga naar onderzoeksmodules"):
                st.session_state.page = "onderzoeksmodules"
                st.rerun()

if __name__ == "__main__":
    case = Case()
    case.main()

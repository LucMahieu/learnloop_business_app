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
            # st.session_state.probleemstelling = 'Bij LearnLoop leidt het gebrek aan duidelijke doelstellingen en KPIs voor klanttevredenheid ertoe dat alle teams ad hoc beslissingen nemen bij het oplossen van klantproblemen, zoals retouren en restituties, wat resulteert in inconsistente klantbeleving en verwarring bij klanten over het retourbeleid.'
            st.session_state.probleemstelling = 'Klanten van LearnLoop zijn ontevreden over het retourbeleid'

        if "overview" not in st.session_state:
            st.session_state.overview = None
        
        if "current_module_index" not in st.session_state:
            st.session_state.current_module_index = 0
        
        if "modules" not in st.session_state:
            st.session_state.modules = self.load_modules()

    def main(self):
        if st.session_state.page == "home":
            self.home_screen()
        elif st.session_state.page == "overview_screen":
            self.overview_screen()
        elif st.session_state.page == "onderzoeksmodules":
            self.onderzoeksmodules()
        elif st.session_state.page == "eindscherm":
            self.eindscherm()
    
    def load_modules(self):
        modules_dir = './data/onderzoeksmodules/'
        modules = []
        for filename in os.listdir(modules_dir):
            if filename.endswith('.json'):
                with open(os.path.join(modules_dir, filename), 'r') as file:
                    module = json.load(file)
                    modules.append(module)
        return modules
    
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
        if os.path.exists('./data/bedrijfsoverzicht.json'):
            with open('./data/bedrijfsoverzicht.json', 'r') as json_file:
                overview_json = json.load(json_file)
                return overview_json
        else:
            return "Overzicht bestand niet gevonden."

    #TODO: probleemstelling moet gekregen worden uit andere scherm
    def generate_overview(self):
        system_message = self.read_prompt('generate_bedrijfsomschrijving')
        user_message = st.session_state.probleemstelling
        print("Generating bedrijfsoverzicht")
        bedrijfsoverzicht_json_response = self.openai_call(system_message, user_message, True)
        with open('./data/bedrijfsoverzicht.json', 'w') as json_file:
           json.dump(bedrijfsoverzicht_json_response, json_file, indent=4)
        print("Succesfully generated and saved bedrijfsoverzicht")
        print("Generating onderzoeksmodules")
        self.generate_onderzoeksmodules(bedrijfsoverzicht_json_response)
        print("Succesfully generated onderzoeksmodules")

        return bedrijfsoverzicht_json_response

    def generate_onderzoeksmodules(self, bedrijfsoverzicht):
        onderzoeksmodules = bedrijfsoverzicht.get("onderzoeksmodules")
        for onderzoeksmodule in onderzoeksmodules:
            self.generate_onderzoeksmodule(onderzoeksmodule)
        st.session_state.modules = self.load_modules()

    def generate_onderzoeksmodule(self, onderzoeksmodule):
        type = onderzoeksmodule.get("type")
        print(f"Generating data for {type}")
        system_message = self.read_prompt(f'generate_{type}')
        user_message = json.dumps(onderzoeksmodule)
        generated_data = self.openai_call(system_message, user_message, True)
        generated_data_path = f'./data/onderzoeksmodules/{type}.json'
        with open(generated_data_path, 'w') as json_file:
            json.dump(generated_data, json_file, indent=4)

    def openai_call(self, system_message, user_message, json_response=False):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        print(f"Started generation with prompt: {system_message[:30]}")
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
        if not os.path.exists('./data/bedrijfsoverzicht.json'):
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
    def onderzoeksmodules(self):
        st.title("Onderzoeksmodules")
        modules = st.session_state.modules
        current_index = st.session_state.current_module_index

        if current_index < len(modules):
            module = modules[current_index]
            self.show_module(module)
        else:
            st.write("Alle modules voltooid!")
        
        col1, col2 = st.columns([1,1])
        if current_index != 0:
            with col1:
                if st.button("Vorige module") and current_index > 0:
                    st.session_state.current_module_index -= 1
                    st.rerun()

        if current_index != len(modules)-1:
            with col2:
                if st.button("Volgende module") and current_index < len(modules) - 1:
                    st.session_state.current_module_index += 1
                    st.rerun()

        if current_index == len(modules)-1:
            with col2:
                if st.button("Naar eindscherm"):
                    st.session_state.page = "eindscherm"
                    st.rerun()

    
    def eindscherm(self):
        st.subheader("Dit is het eindscherm")

    def show_module(self, module):
        module_type = module.get("type")
        if module_type == "cx_prestatiemeting":
            self.show_generate_cx_prestatiemeting_module(module)
        elif module_type == "klantbehoefte_en_gedrag":
            self.show_klantbehoefte_en_gedrag_module(module)
        elif module_type == "organisatiecultuur_analyse":
            self.show_organisatiecultuur_analyse_module(module)
        else:
            st.write("Onbekend module type.")
            st.write(module_type)
        
    def show_generate_cx_prestatiemeting_module(self, module):
        st.header("cx prestatiemodule")
        st.subheader("🔢data hier🔢")
        vraag = module.get("vraag")
        st.subheader(f"vraag: {vraag}")
        st.text_area(label="antwoord")
    
    def show_organisatiecultuur_analyse_module(self, module):
        st.header("organisatiecultuur analyse module")
        st.write(module.get("data"))
        vraag = module.get("vraag")
        st.subheader(f"vraag: {vraag}")
        st.text_area(label="antwoord")
        

    def show_klantbehoefte_en_gedrag_module(self, module):
        st.header("klantbehoefte en gedrag module")
        st.subheader("🔢data hier🔢")
        vraag = module.get("vraag")
        st.subheader(f"vraag: {vraag}")
        st.text_area(label="antwoord:")
    
if __name__ == "__main__":
    case = Case()
    case.main()

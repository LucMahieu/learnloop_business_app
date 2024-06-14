import streamlit as st
import json
import os
from utils.openai_client import connect_to_openai
import pandas as pd
from modules.StakeholderChat import StakeholderChat


class Case:
    def __init__(self):
        self.client = connect_to_openai()
        self.initialize_session_state()

    def initialize_session_state(self):
        if "page" not in st.session_state:
            st.session_state.page = "home"

        if "probleemstelling" not in st.session_state:
            st.session_state.probleemstelling = 'LearnLoop heeft lage NPS scores.'

        if "overview" not in st.session_state:
            st.session_state.overview = None

        if "current_module_index" not in st.session_state:
            st.session_state.current_module_index = 0

        if "modules" not in st.session_state:
            st.session_state.modules = self.load_modules()
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "student_answer" not in st.session_state:
            st.session_state.student_answer = ""

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
        
        st.title("Welkom")
        st.write(f"We gaan werken met een probleemstelling die als basis zal dienen voor de interactieve case. \n\n De standaard probleemstelling is: **{st.session_state.probleemstelling}**")
        
        if st.button("Gebruik deze probleemstelling", use_container_width=True):
            st.session_state.page = "overview_screen"
            st.rerun()
        st.write("Je hebt ook de mogelijkheid om een **eigen probleemstelling** te kiezen en daarmee te werken.")
        probleemstelling_input = st.text_input("Vul hieronder je eigen probleemstelling in:")
        if st.button("Gebruik eigen probleemstelling",use_container_width=True):
            st.session_state.probleemstelling = probleemstelling_input
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

    # TODO: probleemstelling moet gekregen worden uit andere scherm
    def generate_overview(self):
        system_message = self.read_prompt('generate_bedrijfsomschrijving')
        user_message = st.session_state.probleemstelling
        print("Generating bedrijfsoverzicht")
        bedrijfsoverzicht_json_response = self.openai_call(
            system_message, user_message, True)
        with open('./data/bedrijfsoverzicht.json', 'w') as json_file:
            json.dump(bedrijfsoverzicht_json_response, json_file, indent=4)
        print("Succesfully generated and saved bedrijfsoverzicht")
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

    # TODO: Als er al een bedrijfsoverzicht gemaakt is, dan zal deze eerst verwijderd moeten worden.
    def overview_screen(self):
        st.title("Overzicht")
        if not os.path.exists('./data/bedrijfsoverzicht.json'):
            with st.spinner("Een moment, het fictieve bedrijf en de bijbehorende onderzoeksmodules worden gegenereerd..."):
                bedrijfsoverzicht = self.generate_overview()
                print("Generating onderzoeksmodules")
                self.generate_onderzoeksmodules(bedrijfsoverzicht)
                print("Succesfully generated onderzoeksmodules")
            if bedrijfsoverzicht:
                st.rerun()
            else:
                st.write(
                    "Er is een fout opgetreden bij het genereren van het overzicht.")
        else:
            bedrijfsoverzicht = self.load_overview()
            bedrijfsinfo = bedrijfsoverzicht["bedrijfsinfo"]
            naam = bedrijfsinfo["naam"]
            sector = bedrijfsinfo["sector"]
            aantal_werknemers = bedrijfsinfo["aantal_werknemers"]
            bedrijfsomschrijving = bedrijfsinfo["bedrijfsomschrijving"]

            # Displaying the information with Streamlit
            st.title("Bedrijfsinformatie")
            st.write(f"**Naam:** {naam}")
            st.write(f"**Sector:** {sector}")
            st.write(f"**Aantal werknemers:** {aantal_werknemers}")
            st.write(f"**Bedrijfsomschrijving:** {bedrijfsomschrijving}")
            st.write(f"**Probleemstelling:** {st.session_state.probleemstelling}")

            if len(os.listdir('./data/onderzoeksmodules/')) == 0:
                with st.spinner("Een moment geduld, de onderzoeksmodules worden gegenereerd"):
                    print("Generating onderzoeksmodules")
                    self.generate_onderzoeksmodules(bedrijfsoverzicht)
                    print("Succesfully generated onderzoeksmodules")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            if st.button("Ga terug",use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
        with col3:
            if st.button("Ga naar onderzoeksmodules", use_container_width=True):
                st.session_state.page = "onderzoeksmodules"
                st.rerun()

    def onderzoeksmodules(self):
        modules = st.session_state.modules
        current_index = st.session_state.current_module_index

        if current_index < len(modules):
            module = modules[current_index]
            self.show_module(module, modules, current_index)
        else:
            st.write("Alle modules voltooid!")


        # Use a temporary variable for student_answer
        if "student_answer" not in st.session_state:
            st.session_state.student_answer = ""

        if module.get("type") != "stakeholder_chat":
            vraag = module.get("vraag")
            st.subheader(f"{vraag}")
            st.session_state.student_answer = st.text_area(label='', value=st.session_state.student_answer, key="temp_student_answer")

            col1, col2, col3 = st.columns([1,2,1])
            feedback = None
            if current_index != 0:
                with col1:
                    if st.button("Vorige module", use_container_width=True) and current_index > 0:
                        st.session_state.current_module_index -= 1
                        st.session_state.student_answer = ""  # Clear student_answer
                        st.rerun()
            if module.get("type") != "stakeholder_chat":
                with col2:
                    if st.button("Controleer Antwoord", use_container_width=True):
                        with st.spinner("Feedback aan het laden..."):
                            feedback = self.check_answer(
                                module["vraag"], st.session_state.student_answer, module["antwoord"])
                        st.session_state.student_answer = ""  # Clear student_answer
            if current_index != len(modules)-1:
                with col3:
                    if st.button("Volgende module", use_container_width=True) and current_index < len(modules) - 1:
                        st.session_state.current_module_index += 1
                        st.session_state.student_answer = ""  # Clear student_answer
                        st.rerun()
            if feedback is not None:
                st.write(f"{feedback}")

            if current_index == len(modules)-1:
                with col3:
                    if st.button("Naar eindscherm"):
                        st.session_state.page = "eindscherm"
                        st.rerun()
    
    def eindscherm(self):
        st.subheader("Dit is het eindscherm")

    def show_table(self, title, table):
        st.subheader(title.replace("_", " ").capitalize())
        df = pd.DataFrame(table)
        df.set_index(df.columns[0], inplace=True) # To set the first column as the index, for example month
        st.table(df)

    def show_module_tables(self, module):
        st.header(f'Onderzoeksmodule: {module.get("type").replace("_", " ").capitalize()}')
        st.write("Om een goede analyse te maken van de gegevens, is het belangrijk dat je eerst de data zorgvuldig bestudeert en inziet hoe deze met elkaar samenhangen. Dit inzicht zal je helpen om tot een betere eindoplossing te komen.")
        data = module.get("data")

        for title in data:
            self.show_table(title, data[title])
        

    def show_module(self, module, modules, current_index):
        module_type = module.get("type")

        if module_type == "stakeholder_chat":
            col1, col2, col3 = st.columns([1,2,1])
            if current_index != 0:
                with col1:
                    if st.button("Vorige module", use_container_width=True) and current_index > 0:
                        st.session_state.current_module_index -= 1
                        st.session_state.student_answer = ""  # Clear student_answer
                        st.rerun()
            if current_index != len(modules)-1:
                with col3:
                    if st.button("Volgende module", use_container_width=True) and current_index < len(modules) - 1:
                        st.session_state.current_module_index += 1
                        st.session_state.student_answer = ""  # Clear student_answer
                        st.rerun()
            if current_index == len(modules)-1:
                with col3:
                    if st.button("Naar eindscherm"):
                        st.session_state.page = "eindscherm"
                        st.rerun()
            stakeholderChat = StakeholderChat(module.get("naam"), st.session_state.probleemstelling, module)
            stakeholderChat.main()
        else:
            self.show_module_tables(module)


    def check_answer(self, question, student_answer, model_answer):
        prompt = self.read_prompt('feedback_op_vraag')
        user_message = f"""Input:\n
        Vraag: {question}\n
        Antwoord student: {student_answer}\n
        Voorbeeld antwoord: {model_answer}\n"""
        feedback = self.openai_call(prompt, user_message, False)
        return feedback


if __name__ == "__main__":
    case = Case()
    case.main()

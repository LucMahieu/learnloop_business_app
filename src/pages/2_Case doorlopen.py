import streamlit as st
import json
import os
from utils.openai_client import connect_to_openai
import pandas as pd


class Case:
    def __init__(self):
        self.client = connect_to_openai()
        self.initialize_session_state()

    def initialize_session_state(self):
        if "page" not in st.session_state:
            st.session_state.page = "home"

        if "probleemstelling" not in st.session_state:
            # st.session_state.probleemstelling = 'Bij LearnLoop leidt het gebrek aan duidelijke doelstellingen en KPIs voor klanttevreden""eid ertoe dat alle teams ad hoc beslissingen nemen bij het oplossen van klantproblemen, zoals retouren en restituties, wat resulteert in inconsistente klantbeleving en verwarring bij klanten over het retourbeleid.'
            # st.session_state.probleemstelling = 'Klanten van LearnLoop zijn ontevreden over het retourbeleid'
            # st.session_state.probleemstelling = 'Klanten van LearnLoop vinden de site niet duidelijk'
            st.session_state.probleemstelling = 'LearnLoop heeft lage NPS scores'
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
        st.write(
            "Dit is het beginscherm. Klik op de knop hieronder om verder te gaan.")
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
            st.write("Een moment geduld, het overzicht wordt gegenereerd...")
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
            st.write("Dit is het gegenereerde overzicht:")
            bedrijfsoverzicht = self.load_overview()
            st.write(bedrijfsoverzicht)
            if os.listdir('./data/onderzoeksmodules/') == 0:
                print("Generating onderzoeksmodules")
                self.generate_onderzoeksmodules(bedrijfsoverzicht)
                print("Succesfully generated onderzoeksmodules")
        col1, col2 = st.columns([1, 1])
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

        col1, col2 = st.columns([1, 1])
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

    def show_table(self, title, table):
        st.header(title.replace("_", " ").capitalize())
        df = pd.DataFrame(table)
        # df.set_index(df.columns[0], inplace=True) # To set the first column as the index, for example month
        st.table(df)

    def show_module_tables(self, module):
        st.header(module.get("type").replace("_", " ").capitalize())

        data = module.get("data")
        # data = {
        #     "Financiële prestaties": [
        #         {"Maand": "Januari", "CLV (€)": 150, "CAC (€)": 70, "Retention Rate (%)": 65,
        #          "Gross Margin (%)": 25, "ARPU (€)": 20, "Churn Rate (%)": 6},
        #         {"Maand": "Februari", "CLV (€)": 160, "CAC (€)": 68, "Retention Rate (%)": 67,
        #          "Gross Margin (%)": 27, "ARPU (€)": 22, "Churn Rate (%)": 5.8},
        #         {"Maand": "Maart", "CLV (€)": 170, "CAC (€)": 66, "Retention Rate (%)": 68,
        #          "Gross Margin (%)": 28, "ARPU (€)": 24, "Churn Rate (%)": 5.6},
        #         {"Maand": "April", "CLV (€)": 180, "CAC (€)": 64, "Retention Rate (%)": 69,
        #          "Gross Margin (%)": 29, "ARPU (€)": 25, "Churn Rate (%)": 5.4},
        #         {"Maand": "Mei", "CLV (€)": 190, "CAC (€)": 62, "Retention Rate (%)": 71,
        #          "Gross Margin (%)": 30, "ARPU (€)": 27, "Churn Rate (%)": 5.2},
        #         {"Maand": "Juni", "CLV (€)": 200, "CAC (€)": 60, "Retention Rate (%)": 73,
        #          "Gross Margin (%)": 32, "ARPU (€)": 28, "Churn Rate (%)": 5.0}
        #     ]
        # }

        for title in data:
            self.show_table(title, data[title])
        vraag = module.get("vraag")
        st.subheader(f"{vraag}")
        student_answer = st.text_area("Jouw antwoord:")

        # Button to check the answer
        if st.button("Controleer Antwoord"):
            feedback = self.check_answer(
                module["vraag"], student_answer, module["antwoord"])
            st.write(f"{feedback}.")

    def show_module(self, module):
        module_type = module.get("type")
        # module_title = module.get("title")

        if module_type == "chat_stakeholders":
            return
        
        self.show_module_tables(module)
        
        # if module_type == "financiele_data":
        #     

        # if module_type == "cx_prestatiemeting":
        #     self.show_generate_cx_prestatiemeting_module(module)
        # elif module_type == "klantbehoefte_en_gedrag":
        #     self.show_klantbehoefte_en_gedrag_module(module)
        # elif module_type == "organisatiecultuur_analyse":
        #     self.show_organisatiecultuur_analyse_module(module)
        # else:
        #     st.write("Onbekend module type.")
        #     st.write(module_type)

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
        student_answer = st.text_area("Jouw antwoord:")

        # Button to check the answer
        if st.button("Controleer Antwoord"):
            feedback = self.check_answer(
                module["vraag"], student_answer, module["antwoord"])
            st.write(f"{feedback}.")

    def check_answer(self, question, student_answer, model_answer):
        prompt = self.read_prompt('feedback_op_vraag')
        user_message = f"""Input:\n
        Vraag: {question}\n
        Antwoord student: {student_answer}\n
        Voorbeeld antwoord: {model_answer}\n"""
        feedback = self.openai_call(prompt, user_message, False)
        return feedback

    def show_klantbehoefte_en_gedrag_module(self, module):
        st.header("klantbehoefte en gedrag module")
        st.subheader("🔢data hier🔢")
        vraag = module.get("vraag")
        st.subheader(f"vraag: {vraag}")
        st.text_area(label="antwoord:")


if __name__ == "__main__":
    case = Case()
    case.main()

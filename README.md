## Create virtual environment and install requirements
Create a virtual environment named .venv in the current directory using built-in venv module:
````
    py -m venv .venv
````
Set the value of the PYTHONPATH environment variable to the project path:
````
    $env:PYTHONPATH = "C:\path\to\project_folder"
````
Activate the virtual environment on Windows:
````
    .venv\Scripts\activate
````
Install python version at the top of the requirements.txt file:
````
curl -o python-installer.exe https://www.python.org/ftp/python/<version_numer>/python-<version_numer>-amd64.exe
````
Install requirements:
````
    pip install -r requirements.txt
````
To deactivate the virtual environment and return to the original shell environment, run the deactivate command:
````
    deactivate
````
Edit the system environment variables. Create an API key at https://platform.openai.com/account/api-keys.  In the root directory of your project, create a .env file and add your sensitive information there:
ORG_ID=<your-organization-id>
OPENAI_API_KEY=<your-api-key>
## Run Overzicht
Change directory:
````
cd src
````
Run Overzicht.py:
````
    streamlit run Overzicht.py
````
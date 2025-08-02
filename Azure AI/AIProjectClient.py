import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# .env Datei laden
load_dotenv()

project_endpoint = os.getenv("project_endpoint")
project_client = AIProjectClient( 
    credential=DefaultAzureCredential(),
    endpoint=project_endpoint)


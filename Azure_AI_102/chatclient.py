import os
from dotenv import load_dotenv
from openai import AzureOpenAI


try:

    # .env Datei laden
    load_dotenv()

    # Direkte Azure OpenAI Verbindung
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-02-01"
    )
    
    # User input
    user_prompt = input("Enter a question:")
    
    # Chat completion
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    print(response.choices[0].message.content)

except Exception as ex:
    print(ex)
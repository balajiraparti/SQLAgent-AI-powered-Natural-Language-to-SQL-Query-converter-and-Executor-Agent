from google import genai
import asyncio
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()
k=os.getenv("API_KEY")

client = genai.Client(api_key=k)
from google import genai
import os
from dotenv import load_dotenv
import json

load_dotenv()
k = os.getenv("API_KEY")

HISTORY_FILE = "analyze_history.json"

def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def transform_history_for_gemini(history):
    return [
        {"role": msg["role"], "parts": [{"text": msg["content"]}]}
        for msg in history
    ]

history = load_history()
client = genai.Client(api_key=k)

def analyzeQuery(input):
   
        history.append({"role": "user", "content": input})

        response = client.models.generate_content(
                model="gemini-1.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction="""You are a table name identifier for SQL-related natural language queries.

Instructions:

Your job is to analyze each user request and output only the name of the table referenced in the query.

If no table name is mentioned or the request is ambiguous, respond with:

text
INVALID REQUEST
Rules:

Do not include explanations, comments, or extra text.

Do not output SQL queries or any code.

Only output the table name(s) or INVALID REQUEST.

If the request is not related to database operations, respond with INVALID REQUEST.

Never output anything except the table name(s) or INVALID REQUEST. """),
                contents=transform_history_for_gemini(history)
            )
    
        history.append({"role": "model", "content": response.text})
        save_history(history)
        return response.text
            # t = input("Do you want to continue? 1 or 0: ")
            # if t != "1":
            #     break
# while(1):
#      ch=1
#      inp=input("ask:")
#      generateQuery(inp)
#      if(ch==0):
#           break
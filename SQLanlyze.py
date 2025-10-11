from google import genai
import asyncio
from google.genai import types
import os
from dotenv import load_dotenv
import json
load_dotenv()
import streamlit as st

k=os.getenv("API_KEY")
# k = st.secrets["API_KEY"]


client = genai.Client(api_key=k)


# load_dotenv()


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
    valid = []
    for h in history:
        # Safely get and convert content to string
        text = h.get("content")
        if text is None:
            continue  # skip None values entirely

        # Ensure it’s a string before stripping
        if not isinstance(text, str):
            text = str(text)

        text = text.strip()
        if text:  # Only include non-empty text
            valid.append({
                "role": h.get("role", "user"),
                "parts": [{"text": text}]
            })
    return valid

history = load_history()
client = genai.Client(api_key=k)

def analyzeQuery(input):
        print(input)
        history.append({"role": "user", "content": input})

        response = client.models.generate_content(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction = """
You are a Table Name Extractor for SQL-related natural language queries.

Your task: Identify the name(s) of any table(s) mentioned in the user's request.
Respond ONLY with the table name(s) in lowercase, separated by commas if there are multiple.

If the request does not clearly reference any table, respond with:
INVALID REQUEST

### Examples:

User: Create a hotel table  
Output: hotel

User: Show all users in the database  
Output: users

User: Insert a new record into the seminar table  
Output: seminar

User: Delete from employee where id = 5  
Output: employee

User: Remove everything from the system  
Output: INVALID REQUEST

Rules:
- Output only table names, no SQL, no explanations.
- Accept both singular and plural forms (e.g., “users” or “user” → users).
- Be case-insensitive.
- If no table name is found, return exactly:
INVALID REQUEST
"""
),
                contents= [{"role": "user", "parts": [{"text": input}]}]
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
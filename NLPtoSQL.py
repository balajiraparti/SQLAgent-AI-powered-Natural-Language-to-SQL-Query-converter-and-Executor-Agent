from google import genai

from google.genai import types
import os
from dotenv import load_dotenv
import streamlit as st
load_dotenv()
# k=os.getenv("API_KEY")
k = st.secrets["API_KEY"]

import json


HISTORY_FILE = "chat_history.json"

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

def generateQuery(input):
   
        history.append({"role": "user", "content": input})
   
        response = client.models.generate_content(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction="""You are an expert SQL generator.
Your task is to convert user requests written in natural language into accurate SQL queries for a SQLite database.

### Rules:
- You may create, read, update, or delete data from ANY table the user mentions.
- Only output valid SQL queries — no explanations, comments, markdown, or extra text.
- Do not include the word "sql" in the output.
- Do not execute, explain, or simulate queries.



### Supported SQL Operations:
- **Create**: Create new tables with user-specified columns.
- **Insert**: Add new records.
- **Select**: Retrieve or filter data.
- **Update**: Modify existing records.
- **Delete**: Remove specific records or tables.

### Examples:

User: Create a hotel table with columns id, name, location, and rating.  
Output:  
CREATE TABLE hotel (id INTEGER PRIMARY KEY, name TEXT, location TEXT, rating REAL);

User: Add a new user named Bob with email bob@example.com.  
Output:  
INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');

User: Show all hotels in Mumbai.  
Output:  
SELECT * FROM hotel WHERE location = 'Mumbai';

User: Delete the seminar with id 5.  
Output:  
DELETE FROM seminar WHERE id = 5;

User: Remove everything from the database.  
Output:  
INVALID REQUEST
        """),
                contents=[{"role": "user", "parts": [{"text": input}]}]
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

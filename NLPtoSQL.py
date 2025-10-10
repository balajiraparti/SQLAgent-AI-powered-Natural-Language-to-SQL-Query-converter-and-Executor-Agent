from google import genai
import asyncio
from google.genai import types
import os
from dotenv import load_dotenv
import streamlit as st
load_dotenv()
# k=os.getenv("API_KEY")
k = st.secrets["API_KEY"]
# client = genai.Client(api_key=k)
from google import genai
import os
from dotenv import load_dotenv
import json

# load_dotenv()
# k = "API_KEY"
# k = os.getenv("API_KEY")

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
        Your job is to convert user requests written in natural language into accurate SQL queries for a SQLite database.
        Instructions:
        always add data to table named users.
        Respond with only the SQL query, and nothing else.
        Do not include "sql" word in the output response message.
        Do not include explanations, comments, or extra text.

        Only output valid SQL for the described request.

        If the input is ambiguous, incomplete, or does not map to a valid SQL query, respond with only:
        INVALID REQUEST

        Do not execute, explain, or comment on the query.

        Do not output anything except the SQL query.

        Handle all CRUD operations:

        Create: Table creation, inserting new records.

        Read: Selecting, filtering, sorting, and aggregating data.

        Update: Modifying existing records.

        Delete: Removing records or tables.

        Edge Cases:

        If a field or table is not specified, or the request is unclear, respond with INVALID REQUEST.

        If the request is not related to database operations, respond with INVALID REQUEST.

        If the request asks for something dangerous (like dropping all tables), respond with INVALID REQUEST.

        Negative Prompts:

        Never output explanations, comments, or extra text.

        Never execute or simulate the query.

        Never output anything except the SQL code or INVALID REQUEST.

        Examples:

        User: Add a new user named Bob with email bob@example.com.
        Output:

        INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');
        User: Show all users.
        Output:

     
        SELECT * FROM users;
        User: Change Alice's email to alice@newmail.com.
        Output:

     
        UPDATE users SET email = 'alice@newmail.com' WHERE name = 'Alice';
        User: Delete the user with id 5.
        Output:

       
        DELETE FROM users WHERE id = 5;
        User: Make me a sandwich.
        Output:
        INVALID REQUEST

        User: Remove everything from the database.
        Output:
        INVALID REQUEST

        User:
        Output:
        INVALID REQUEST 
        dont use sql word in response
        text    """),
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
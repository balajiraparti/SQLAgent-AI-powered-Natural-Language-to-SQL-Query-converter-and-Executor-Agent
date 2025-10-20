import sqlite3
import NLPtoSQL as n
import SQLanlyze as s
import re
import table_names as t
import json
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()
# k=os.getenv("API_KEY")
k = st.secrets["API_KEY"]
SQLexecutor = {
    "name": "execute_query",
    "description": "Generates and Executes SQL query based on user input written in natural language on local SQlite database.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
      
                "description": "input written in natural language(English,Hindi)",
            }
        },
        "required": ["query"],
    },
}
SQLdisplay = {
    "name": "display_users",
    "description": "Display the contents of a specified table from the local SQLite database",
    "parameters": {
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
      
                "description": "Table name to display",
            }
        },
        "required": ["table_name"],
    },
}
client = genai.Client(api_key=k)
tools = types.Tool(function_declarations=[SQLexecutor,SQLdisplay])
config = types.GenerateContentConfig(tools=[tools])

class SQLagent:
    def __init__(self):
        self.table_name=""
        self.json_file_path="chat_history.json"
        self.is_query_executed=False
        self.patterns = [
        r"CREATE TABLE\s+(\w+)",                   # e.g., CREATE TABLE hotel
        r"INSERT INTO\s+(\w+)",                    # e.g., INSERT INTO hotel
        r"UPDATE\s+(\w+)",                         # e.g., UPDATE hotel SET ...
        r"DELETE FROM\s+(\w+)"                     # e.g., DELETE FROM hotel WHERE ...
    ] 
        self.tables=[]
        st.session_state.query=""
        self.o=t.TableNameManager()

    def remove_sql_word(self,text):
        # Remove leading and trailing triple backticks
        cleaned = re.sub(r"^\s*```(?:sql)?\s*|\s*```$", "", text, flags=re.IGNORECASE)

        # Remove standalone 'sql' word (case-insensitive)
        cleaned = re.sub(r"\bsql\b", "", cleaned, flags=re.IGNORECASE)

        # Strip leading/trailing whitespace
        return cleaned.strip()
    def get_last_table_name_from_json(self):
        with open(self.json_file_path, 'r') as file:
            data = json.load(file)

        last_table_name = None

       
        for entry in reversed(data):
            if entry["role"] == "model":
                content = entry["content"].strip()

                for pattern in self.patterns:
                    match = re.match(pattern, content, re.IGNORECASE)
                    if match:
                        last_table_name = match.group(1)
                        return last_table_name
        return None

    def execute_query(self,query):
        """Execute a natural language-based SQL query on the local SQLite database.

    This method takes a user query (in natural language), retrieves it from
    Streamlit session state (`st.session_state.query`), and converts it into an
    executable SQL statement using a natural language to SQL generator (`n.generateQuery()`).
    It then sanitizes the generated query to remove redundant SQL keywords,
    analyzes the SQL statement to determine the target table name through
    `s.analyzeQuery()`, and marks the query as executed.

    If the analyzed table name is invalid, an "Invalid request" message is displayed.
    Otherwise, the method checks whether the referenced table exists in the database
    using `self.o.table_exists()`. If it does not, a new table is automatically created
    via `self.o.add_table()`.

    Once validated, the SQL query is executed against the local SQLite database
    (`mydatabase.db`) inside a context manager, ensuring automatic connection handling
    and commit management. Upon successful execution, a confirmation message is
    displayed in the Streamlit UI. If any exception occurs (e.g., due to malformed
    SQL or schema mismatch), the user is informed that the query failed.

    Args:
        query (str): The user input query (natural language or SQL) used to generate
            the final executable SQL statement.

    Returns:
        None. Outputs messages to the Streamlit interface:
            - "Query executed successfully" when the SQL runs correctly.
            - "Invalid request" if the generated query cannot be processed.
            - "Wrong query, please try again!" when execution fails due to an error.
    """
        q=st.session_state.query
        res=n.generateQuery(q)
        print(res)
        res=self.remove_sql_word(res)
        print(res)
        self.table_name=s.analyzeQuery(res)
        self.is_query_executed=True

        print(self.table_name)
        if(self.table_name =="INVALID REQUEST"):
            # print("Invalid request")
            st.write("Invalid request")
            return
        try:
            if not self.o.table_exists( self.table_name ):
                self.o.add_table(self.table_name)

            with sqlite3.connect('mydatabase.db') as conn:
                cur = conn.cursor()
                cur.execute(res)
                conn.commit()
                # print("Query executed successfully")
                st.write("Query excuted successfully")
        except Exception as e:
            # print("wrong query,please try again:", e)
            st.write("table might be existed or wrong query,please try again!")
   


    def display_users(self,table_name):
        """Display the contents of a specified table from the local SQLite database.

    This method retrieves the table name from Streamlit session state
    (`st.session_state.display`) and displays its data both in the console and
    within the Streamlit interface. It first validates whether the user has provided
    a valid table name and ensures that the referenced table exists in the connected
    SQLite database (`mydatabase.db`). If no table name is provided or the table does
    not exist, an appropriate Streamlit message is displayed and execution stops.

    When a valid table is found, the method establishes a connection to the SQLite
    database and executes a `SELECT * FROM <table_name>` query to fetch all rows.
    It extracts column headers from the cursor metadata, retrieves all table records,
    and constructs a pandas DataFrame for structured visualization. The resulting
    table is displayed in the Streamlit UI using `st.table()`, and the same data,
    including column names and rows, is printed to the console for debugging or
    logging purposes.

    Args:
        None. Uses the table name stored in `st.session_state.display` as input.

    Returns:
        None. Displays the table contents in the Streamlit interface or
        outputs an appropriate message when no table is found.
    """  

        # self.table_name=st.session_state.display
        print(table_name)
        if table_name == "":
             st.write("Enter table name to display:")
             return
        # k=st.session_state.query
        # self.table_name=s.analyzeQuery(k)
        # print(self.table_name)
        # self.table_name=input("Enter Table name:")
        # # print(self.table_name)
        # self.table_name=st.text_input("Enter Table name:")
        if( not self.o.table_exists(table_name)):
            st.write("table not found")
            return
        print(self.o.display_tables())
        # if(self.is_query_executed==False):
            
        #     self.table_name=self.get_last_table_name_from_json()
        # if(self.table_name not in self.tables):
        #         print("No table found")
        #         return
        print(self.tables)
        with sqlite3.connect('mydatabase.db') as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table_name}")
                    # Fetch column names from cursor description
            column_names = [desc[0] for desc in cur.description]
            # Fetch all rows from the query
            rows = cur.fetchall()
            df = pd.DataFrame(rows, columns=column_names)
            st.table(df)
            # Print column headers
            print(" | ".join(column_names))
            print("-" * (len(" | ".join(column_names))))
            
            # Print each row
            for row in rows:
                print(" | ".join(str(item) for item in row))
            # rows = cur.fetchall()
            # for row in rows:
            #     print(row)
           


def main():
    sqlagent=SQLagent()
    
    user_input = st.text_input("Enter your query:", key="user_input")
   
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "display" not in st.session_state:
        st.session_state.display = ""
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False
    if st.button("Execute query",key="execute_button"):
        st.session_state.button_clicked = True

    if user_input:
        if st.session_state.button_clicked:
            st.session_state.query=user_input
            print(st.session_state.query)
            # print(user_input)
            contents = [
    types.Content(
        role="user", parts=[types.Part(text=user_input)]
    )
]
            # sqlagent.execute_query()
            response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=config,
)
            tool_call = response.candidates[0].content.parts[0].function_call

            if tool_call == None:
                st.write("Invalid request")
            elif tool_call.name == "execute_query":
                sqlagent.execute_query(**tool_call.args)
            elif tool_call.name == "display_users":
                sqlagent.display_users(**tool_call.args)
            
                
            # if st.button("Execute query"):
            #     sqlagent.execute_query()

    # display_input=st.text_input("Enter table name to display:",key="display_input")
    # if display_input:
    #     # if st.button("display table"):
    #         st.session_state.display=display_input
    #         print(st.session_state.display) 

    #         if st.button("display table"):
    #                 sqlagent.display_users()
    # print(sqlagent.o.table_names)
    # print(sqlagent.o.table_exists("hotel"))
    # sqlagent.o.display_tables()
    # print(sqlagent.tables)

if __name__ == "__main__":
    main()

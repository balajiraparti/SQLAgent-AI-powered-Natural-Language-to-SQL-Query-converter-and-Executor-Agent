import sqlite3
import NLPtoSQL as n
import SQLanlyze as s
import re
import table_names as t
import json
import streamlit as st
import pandas as pd
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

    def execute_query(self):
        q=st.session_state.query
    
        res=n.generateQuery(q)
        print(res)
        res=self.remove_sql_word(res)
        print(res)
        self.table_name=s.analyzeQuery(res)
        # self.is_query_executed=True

        print(self.table_name)
        if(self.table_name=="INVALID REQUEST"):
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
            st.write("wrong query,please try again!")
   


    def display_users(self):
        self.table_name=st.session_state.display
        # k=st.session_state.query
        # self.table_name=s.analyzeQuery(k)
        # print(self.table_name)
        # self.table_name=input("Enter Table name:")
        # # print(self.table_name)
        # self.table_name=st.text_input("Enter Table name:")
        if( not self.o.table_exists(self.table_name)):
            st.write("not table found")
            return
        # if(self.is_query_executed==False):
            
        #     self.table_name=self.get_last_table_name_from_json()
        # if(self.table_name not in self.tables):
        #         print("No table found")
        #         return
        print(self.tables)
        with sqlite3.connect('mydatabase.db') as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {self.table_name}")
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
    if user_input:
        if st.button("Execute query"):
            st.session_state.query=user_input
            print(st.session_state.query)
            sqlagent.execute_query()

    display_input=st.text_input("Enter table name to display:",key="display_key")
    if display_input:
        if st.button("display table"):
            st.session_state.display=display_input
            print(st.session_state.display)    
            sqlagent.display_users()
    # print(sqlagent.o.table_names)
    # print(sqlagent.o.table_exists("hotel"))
    # sqlagent.o.display_tables()
    # print(sqlagent.tables)

if __name__ == "__main__":
    main()

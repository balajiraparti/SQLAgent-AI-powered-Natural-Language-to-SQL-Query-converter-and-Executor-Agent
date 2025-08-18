import pickle
import os

class TableNameManager:
    def __init__(self, filename='table_names.pkl'):
        self.filename = filename
        self.table_names = self.load_table_names()
    
    def load_table_names(self):
        """Load table names from pickle file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'rb') as f:
                    return pickle.load(f)
            except (pickle.PickleError, EOFError):
                return []
        return []
    
    def save_table_names(self):
        """Save table names to pickle file"""
        with open(self.filename, 'wb') as f:
            pickle.dump(self.table_names, f)
    
    def table_exists(self, table_name):
        """Check if a table name exists in the list"""
        # Fix: Use stripped name for comparison
        return table_name.strip() in [name.strip() for name in self.table_names]
    
    def check_table_existence(self, table_name):
        """Check if table exists and print status"""
        if self.table_exists(table_name):
            print(f"Table '{table_name.strip()}' exists in the file")
            return True
        else:
            print(f"Table '{table_name.strip()}' does not exist in the file")
            return False
    
    def add_table(self, table_name):
        """Add a table name to the list"""
        clean_name = table_name.strip()
        if not self.table_exists(clean_name):
            self.table_names.append(clean_name)  # Fix: Add cleaned name
            self.save_table_names()
            print(f"Added table: {clean_name}")
            return True
        else:
            print(f"Table {clean_name} already exists")
            return False
    
    def remove_table(self, table_name):
        """Remove a table name from the list"""
        clean_name = table_name.strip()
        if self.table_exists(clean_name):
            # Remove by stripped name
            self.table_names = [name for name in self.table_names if name.strip() != clean_name]
            self.save_table_names()
            print(f"Removed table: {clean_name}")
            return True
        else:
            print(f"Table {clean_name} not found")
            return False
    
    def get_tables(self):
        """Get all table names"""
        return self.table_names
    
    def display_tables(self):
        """Display all table names"""
        if self.table_names:
            print("Current tables:")
            for i, table in enumerate(self.table_names, 1):
                print(f"{i}. {table.strip()}")  # Show without \n or whitespace
        else:
            print("No tables found")

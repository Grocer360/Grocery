
# config.py

import os
import json
import psycopg2

class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = os.path.join(os.path.dirname(__file__), config_file)
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Configuration file {self.config_file} not found.")
            self.config = {}

    def get(self, key, default=None):
        return self.config.get(key, default)

def get_db_connection():
    conn_details = {
        'dbname': "okzegkwz",
        'user': "okzegkwz",
        'password': "7UwFflnPy3byudSr32K1ugHniRSVK6v_",
        'host': "kandula.db.elephantsql.com",
        'port': "5432"
    }
    try:
        conn = psycopg2.connect(**conn_details)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

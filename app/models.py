import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), 'database.json')

def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"accounts": {}}, f)
    with open(DB_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

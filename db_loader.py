import sqlite3
import json
import os

# Forces the loader to use the folder where the script actually lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "wicked_tactical.db")
JSON_INPUT = os.path.join(BASE_DIR, "cmn4_interface_control.json")

def load_json_to_db():
    print(f"[INIT] Target Database: {DB_PATH}")
    
    if not os.path.exists(JSON_INPUT):
        print(f"[ERROR] Could not find {JSON_INPUT}. Run wicked_scraper.py first!")
        return

    try:
        # Connect to the EXACT path the terminal uses
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Wipe and Rebuild
        cursor.execute("DROP TABLE IF EXISTS tactical_rules")
        cursor.execute('''
            CREATE TABLE tactical_rules (
                id TEXT,
                name TEXT,
                bits INTEGER,
                type TEXT
            )
        ''')

        with open(JSON_INPUT, 'r') as f:
            data = json.load(f)
            for entry in data:
                cursor.execute('''
                    INSERT INTO tactical_rules (id, name, bits, type)
                    VALUES (?, ?, ?, ?)
                ''', (entry['id'], entry['name'], entry['bits'], entry['type']))

        conn.commit()
        conn.close()
        print(f"[SUCCESS] Ingested {len(data)} rules into the WICKED backend database.")
        
    except Exception as e:
        print(f"[ERROR] Database injection failed: {e}")

if __name__ == "__main__":
    load_json_to_db()
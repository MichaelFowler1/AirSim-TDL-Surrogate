import json
import sqlite3
import time
import os
import sys
from datetime import datetime

# --- PATH LOGIC: Forces the script to find files in its own folder ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "wicked_tactical.db")
JSON_PATH = os.path.join(BASE_DIR, "live_mids_stream.json")

def get_decoding_rules():
    if not os.path.exists(DB_PATH):
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, bits, type FROM tactical_rules")
        rules = cursor.fetchall()
        conn.close()
        return rules
    except sqlite3.OperationalError:
        return None

def display_terminal():
    print(f"[INIT] Searching for DB at: {DB_PATH}")
    
    while True:
        rules = get_decoding_rules()
        
        if rules is None:
            print("[ERROR] Database found but table 'tactical_rules' is missing.")
            print("        Try running: python db_loader.py")
            time.sleep(5)
            continue

        if os.path.exists(JSON_PATH):
            try:
                with open(JSON_PATH, "r") as f:
                    data = json.load(f)
                
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f" === TACTICAL DISPLAY: {data['callsign']} ===")
                print(f" Track ID:  [{data['track_number']}]")
                print(f" Platform:  {data['platform']}")
                print(f" System Time: {datetime.now().strftime('%H:%M:%S')}")
                print("-" * 50)
                print(f" ALT: {data['alt_msl']:,.0f}ft | SPD: {data['velocity_kts']:.1f}kts")
                print("-" * 50)
                print(" Active Decoding Rules (from DB):")
                for rule in rules:
                    print(f"  [Rule] {rule[0]}: {rule[1]} bits ({rule[2]})")
            except Exception as e:
                pass # Skip a frame if file is being written to
        else:
            print("\r[WAIT] Awaiting MIDS Stream (Run flight_spoofer.py)...", end="")
            
        time.sleep(1)

if __name__ == "__main__":
    try:
        display_terminal()
    except KeyboardInterrupt:
        print("\n[STOP] Tactical Terminal Offline.")
        sys.exit(0)
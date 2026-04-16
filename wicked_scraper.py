import re
import json

def scrape_rules():
    print("[INIT] Opening target specification: mock_cmn4_spec.txt")
    print(" Parsing EA-18G Link 16 specifications...\n")
    rules = []
    
    # The upgraded Regex pattern designed to hunt down the "|" dividers
    pattern = re.compile(r"Field\s+(.*?)\s*\|\s*(.*?)\s*\|\s*(\d+)\s*bits\s*\|\s*(.*?)\s*\|")
    
    try:
        with open("mock_cmn4_spec.txt", "r") as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    # THE FIX: Exactly matching the keys db_loader.py expects
                    rules.append({
                        "id": match.group(1).strip(),
                        "name": match.group(2).strip(),
                        "bits": int(match.group(3)),
                        "type": match.group(4).strip()
                    })
        
        print("[EXPORT] Saving Digital ICD to cmn4_interface_control.json...")
        with open("cmn4_interface_control.json", "w") as out_file:
            json.dump(rules, out_file, indent=4)
            
        print(f"Extraction complete. {len(rules)} fields secured.")
        
    except FileNotFoundError:
        print("[ERROR] Could not find mock_cmn4_spec.txt")

if __name__ == "__main__":
    scrape_rules()
"""File loading and path-handling functions for HarborFlow.

Create reusable JSON and CSV loaders here. Do not hard-code sample records.
"""
import json
import os
import csv
script_dir = os.path.dirname(os.path.abspath(__file__)) #directory the main.py is in. The assumption is the dataset will be in the same directory.


INCIDENTS_DIR = os.path.join(script_dir, "dataset", "incidents")
MANIFESTS_DIR = os.path.join(script_dir, "dataset", "manifests")
PORT_CALLS_FILE = os.path.join(script_dir, "dataset", "port_calls.csv")
SANITIZED_DIR = os.path.join(script_dir, "exports", "sanitized")


def load_json(directory): 
    damaged_files = 0
    list_of_dicts = []

    for file_name in os.listdir(directory): 
        if file_name.endswith(".json"):
            file_path = os.path.join(directory, file_name)
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)  
                    list_of_dicts.append(data)
                except json.JSONDecodeError as e:
                    damaged_files += 1  
    return list_of_dicts, damaged_files

def load_csv(directory, vessel_id):
    list_of_calls = []

    filename = os.path.join(script_dir, "dataset", "port_calls.csv")
    with open(filename,"r") as file:
        reader = csv.reader(file)
        rows = list(reader) 
    
    for call in rows: 
        
        if vessel_id == call[1]:
            list_of_calls.append(call)

    return list_of_calls

def load_incidents():
    records, skipped = load_json(INCIDENTS_DIR)
    incidents = []
    for data in records:
        if (isinstance(data, dict)
                and isinstance(data.get("incident_id"), str)
                and isinstance(data.get("title"), str)
                and isinstance(data.get("report"), str)):
            incidents.append(data)
        else:
            skipped += 1
    return incidents, skipped


def save_sanitized_report(incident_id, text):
    os.makedirs(SANITIZED_DIR, exist_ok=True)
    path = os.path.join(SANITIZED_DIR, f"{incident_id}-sanitized.txt")
    with open(path, "w", encoding="utf-8", newline="") as file:
        file.write(text)
    return path



def port_call_exists(call_id):
    try:
        with open(PORT_CALLS_FILE, "r", newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                if (row.get("call_id") or "").strip().lower() == call_id.lower():
                    return True
    except FileNotFoundError:
        pass
    return False


def load_manifest_by_call_id(call_id):
    manifests, _ = load_json(MANIFESTS_DIR)
    for data in manifests:
        if isinstance(data, dict) and str(data.get("call_id", "")).strip().lower() == call_id.lower():
            if isinstance(data.get("event_codes"), list):
                return data
            return None
    return None

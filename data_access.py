"""File loading and path-handling functions for HarborFlow.

Create reusable JSON and CSV loaders here. Do not hard-code sample records.
"""
import json
import os
import csv
from pathlib import Path
script_dir = os.path.dirname(os.path.abspath(__file__)) #directory the main.py is in. The assumption is the dataset will be in the same directory.


INCIDENTS_DIR = os.path.join(script_dir, "dataset", "incidents")
MANIFESTS_DIR = os.path.join(script_dir, "dataset", "manifests")
PORT_CALLS_FILE = os.path.join(script_dir, "dataset", "port_calls.csv")
SANITIZED_DIR = os.path.join(script_dir, "exports", "sanitized")
PROJECT_FOLDER = Path(__file__).resolve().parent
DATASET_FOLDER = PROJECT_FOLDER / 'dataset'
EXPORTS_FOLDER = PROJECT_FOLDER / 'exports'

# Task 8 and Task 9 file paths
WEATHER_FILE = os.path.join(script_dir, "dataset", "weather.csv")
INCIDENT_INDEX_FILE = os.path.join(
    script_dir, "dataset", "incident-index.json"
)

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



def read_json_records(folder):
    records = []
    for path in sorted((DATASET_FOLDER / folder).glob('*.json')):
        try:
            with path.open(encoding='utf-8-sig') as file:
                data = json.load(file)
            for item in data if isinstance(data, list) else [data]:
                if isinstance(item, dict):
                    records.append(item)
                else:
                    print(f'Skipping invalid record in {path.name}.')
        except (OSError, ValueError) as error:
            print(f'Skipping {path.name}: {error}')
    return records


def read_json_files():
    return read_json_records('shipments')


def read_portcalls():
    with (DATASET_FOLDER / 'port_calls.csv').open(encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))

#Task 8 and 9

def load_port_call_records():
    """Read port_calls.csv as a list of dictionaries, one per row."""
    with open(PORT_CALLS_FILE, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def load_weather_records():
    """Read weather.csv as a list of dictionaries, one per row."""
    with open(WEATHER_FILE, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def incident_source_files():
    """Return all source incident JSON files in a stable order."""
    if not os.path.isdir(INCIDENTS_DIR):
        return []

    paths = []
    for filename in os.listdir(INCIDENTS_DIR):
        path = os.path.join(INCIDENTS_DIR, filename)
        if filename.lower().endswith(".json") and os.path.isfile(path):
            paths.append(path)
    return sorted(paths)


def incident_index_is_current():
    """A cache is current when it exists and is not older than any source file."""
    if not os.path.isfile(INCIDENT_INDEX_FILE):
        return False
    if not os.path.isdir(INCIDENTS_DIR):
        return False

    try:
        cache_time = os.path.getmtime(INCIDENT_INDEX_FILE)
        for path in incident_source_files():
            if cache_time < os.path.getmtime(path):
                return False
    except OSError:
        return False

    return True


def _valid_incident_index(data):
    """Check that the cached JSON has the structure required by Task 9."""
    if not isinstance(data, dict) or set(data.keys()) != {"index", "titles"}:
        return False

    word_index = data["index"]
    titles = data["titles"]
    if not isinstance(word_index, dict) or not isinstance(titles, dict):
        return False

    for word, incident_ids in word_index.items():
        if not isinstance(word, str) or not isinstance(incident_ids, list):
            return False
        if any(not isinstance(incident_id, str) for incident_id in incident_ids):
            return False
        if len(incident_ids) != len(set(incident_ids)):
            return False

    for incident_id, title in titles.items():
        if not isinstance(incident_id, str) or not isinstance(title, str):
            return False

    # Every indexed incident needs a title for search results.
    for incident_ids in word_index.values():
        if any(incident_id not in titles for incident_id in incident_ids):
            return False

    return True


def load_incident_index_cache():
    """Load a usable index cache, or return None if it needs rebuilding."""
    if not incident_index_is_current():
        return None

    try:
        with open(INCIDENT_INDEX_FILE, "r", encoding="utf-8") as file:
            cached_data = json.load(file)
    except (OSError, json.JSONDecodeError, UnicodeError):
        return None

    if not _valid_incident_index(cached_data):
        return None

    return cached_data


def save_incident_index_cache(index_data):
    """Write the index cache through a temporary file to avoid half-written JSON."""
    os.makedirs(os.path.dirname(INCIDENT_INDEX_FILE), exist_ok=True)
    temporary_path = INCIDENT_INDEX_FILE + ".tmp"

    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(index_data, file, indent=2, sort_keys=True)
        file.write("\n")

    os.replace(temporary_path, INCIDENT_INDEX_FILE)
    return INCIDENT_INDEX_FILE

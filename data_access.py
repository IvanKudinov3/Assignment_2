"""File loading and path-handling functions for HarborFlow.

Create reusable JSON and CSV loaders here. Do not hard-code sample records.
"""
import json
import os
import csv
script_dir = os.path.dirname(os.path.abspath(__file__)) #directory the main.py is in. The assumption is the dataset will be in the same directory.
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
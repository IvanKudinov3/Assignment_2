import json
import os
import csv
from datetime import datetime

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
                    print(f"Total damaged files: {damaged_files}")
    return list_of_dicts

def load_csv(directory, vessel_id):
    list_of_calls = []

    filename = os.path.join(script_dir, "dataset", "port_calls.csv")
    with open(filename,"r") as file:
        reader = csv.reader(file)
        rows = list(reader) 
    
    for call in rows: 
        print(call[1])
        if vessel_id == call[1]:
            list_of_calls.append(call) 
    print(list_of_calls,"list of calls with matchin ids")

    return list_of_calls

def get_vessel_name(vessel):
    return vessel['name']

def sort_vessels_alphabetically(vessels):
    sorted_vessels = sorted(vessels, key=get_vessel_name) #key expects a function and with each vessel we give a key, name of the vessel
    return sorted_vessels


def load_vessels(): 
    path_vessels = os.path.join(f"{script_dir}/dataset/vessels")

    vessels = load_json(path_vessels)  
    vessels = sort_vessels_alphabetically(vessels)
    
    return vessels #returns a list of dictionaries of vessels

def list_registered_vessels(vessels):
    i = 0
    for v in vessels:
        print(f"- {v['name']} | IMO {v['imo']} | {v['capacity_teu']} TEU")
        i += 1
    

def inspect_vessel_manifest(vessels_name, date): 
    #vessels_name = input("Vessel name: ").strip()
    #date = input("Type in a reference date in the following format YYYY-MM-DD: ").strip()
    date = datetime.strptime(date, "%Y-%m-%d").date()
    filename = os.path.join(script_dir, "dataset", "port_calls.csv")
    vessels = load_vessels()
    id = ""
    for v in vessels:
        if vessels_name == v['name']:
            id = v['vessel_id']
    print(id, "list of ids") 
    port_calls = load_csv(filename, id) #list of calls of a vessel with a given ID
    for row in port_calls:
            row[3] = datetime.strptime(row[3], "%Y-%m-%d").date()
    for calls in port_calls:
        if date >= calls[3]:
            port_calls = calls
        if date == calls[3]:
            port_calls = sort_alphabetically(port_calls)

    
    #port_calls = sort_port_calls_by_date(port_calls)
    
    return port_calls[0] 

def get_port_call_date(call):
    return call[3]

def sort_port_calls_by_date(calls):
    #before sorting, I need to turn the dates into date data format
    for row in calls:
        row[3] = datetime.strptime("%Y-%m-%d").date()
    sorted_calls = sorted(calls, key=get_port_call_date)
    print(sorted_calls, "SORTED CALLS")

    return sorted_calls


def main(): 
    inspect_vessel_manifest("Nordic Relay", "2026-10-18")
    
        #load_csv("", )

if __name__ == "__main__":
    main()
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
    print(vessels,"VESSELS")
    return vessels #returns a list of dictionaries of vessels

def display_registered(vessels): 
    print(vessels)
    for v in vessels:
        print(f"- {v['name']} | IMO {v['imo']} | {v['capacity_teu']} TEU") 


 
def find_id_in_port_calls(vessels_name, reference_date): 
    #vessels_name = input("Vessel name: ").strip()
    #reference_date = input("Type in a reference date in the following format YYYY-MM-DD: ").strip()

    try:
        reference_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
    except ValueError:
        print("Error - Date must use YYYY-MM-DD.")
        return
    
    filename = os.path.join(script_dir, "dataset", "port_calls.csv")
    vessels = load_vessels()
    id = ""
    for v in vessels:
        if vessels_name.lower() == v['name'].lower():
            id = v['vessel_id'] 
    port_calls = load_csv(filename, id) #list of calls of a vessel with a given ID    
    if id is "":
        print("Vessel not found.")
    calls_to_sort = [] #list of ids to sort alphabetically if they have the same date 
    try:
        for call in port_calls:
            corrected_date = datetime.strptime(call[3], "%Y-%m-%d").date()
            call[3] = corrected_date
            if call[3] >= reference_date: #
                calls_to_sort.append(call) 
    except ValueError:
        print("Error - one of the dates in Port Calls is incorrect")
        return
    
    if not calls_to_sort:
        print("No upcoming port calls found.")
        return
    
    port_call = min(calls_to_sort, key=get_port_call_date)
    
    return port_call[0]

def get_port_call_date(call):
    return (call[3], call[0])

def sort_port_calls(calls): 
    sorted_calls = sorted(calls, key=get_port_call_date) #sorts the calls by date first and then alphabeticaly by id
    print(sorted_calls, "SORTED CALLS")

    return sorted_calls[0]

def get_matching_manifests(port_call_id):
    calls_id = port_call_id[0]
    manifest_directory = f"{script_dir}/dataset/manifest"
    list_manifests = load_json(manifest_directory) 

    found_manifest = None
    for manifest in list_manifests:
        if calls_id == manifest["call_id"]:
            found_manifest = manifest
    if found_manifest == None:
        print("Manifest unavailable")
        return
    print(found_manifest)
    return found_manifest

def get_matching_shipments(dict_manifest):
    shipment_ids = dict_manifest["shipment_ids"]
    shipment_directory = f"{script_dir}/dataset/manifest"
    list_shipments = load_json(shipment_directory)

    list_sorted_shipments = []
    for shipment in list_shipments:
        shipment_id_to_compare = shipment[0]
        for id in shipment_ids:
            if shipment_id_to_compare == id:
                list_sorted_shipments.append(shipment)

    return list_sorted_shipments

def inspect_vessel_manifest(name, date):
    calls_id = find_id_in_port_calls(name, date)
    matching_manifest = get_matching_manifests(calls_id)
    list_matching_shipments = get_matching_shipments(matching_manifest)
    formated_date = datetime.strptime(date, "%d %B %Y")

    
    
    print(f"Manifest for {name} | Call {calls_id} | {date}")
    for shipmet in list_matching_shipments:
        print()
    

def main(): 
    find_id_in_port_calls("Nordic Relay", "2026-10-18")

    #display_registered(load_vessels())

if __name__ == "__main__":
    main()
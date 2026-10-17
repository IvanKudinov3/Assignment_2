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
        if vessel_id == call[1]:
            list_of_calls.append(call)

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

def display_registered_vessels(vessels): 
    for v in vessels:
        print(f"- {v['name']} | IMO {v['imo']} | {v['capacity_teu']} TEU") 


# finds id in the port call in accordance with the vessels name, then sorts the calls by date and alphabetically if needed. 
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
    if id == "":
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

    return sorted_calls[0]

#retrieves the manifests from the dataset and sorts them according with the vessels id.
def get_matching_manifests(port_call_id):
    calls_id = port_call_id
    manifest_directory = f"{script_dir}/dataset/manifests"
    list_manifests = load_json(manifest_directory) 

    found_manifest = None
    for manifest in list_manifests:
        if calls_id == manifest["call_id"]:
            found_manifest = manifest
    if found_manifest == None:
        print("Manifest unavailable")
        return 
    return found_manifest

#retrieves the shipments which ids match with the ids in the manifest 
def get_matching_shipments(dict_manifest):
    
    shipment_ids_in_manifest = dict_manifest["shipment_ids"]
    shipment_directory = f"{script_dir}/dataset/shipments"
    list_of_dicts_shipments = load_json(shipment_directory)

    found_shipments = []
    missing_shipments = []
    num_missing_shipments = 0
    num_declared_shipments = len(shipment_ids_in_manifest) 
    
    for id in shipment_ids_in_manifest: 
        found = False #the id was not found 
        for shipment in list_of_dicts_shipments:
            if id == shipment["shipment_id"]: 
                #check if every key is in the shipment dict. If it is not, add it and give it a string "NOT PROVIDED" or False where appropriate
                if 'hazardous' not in shipment:
                    shipment['hazardous'] = False
                if 'temperature_controlled' not in shipment:
                    shipment['temperature_controlled'] = False
                if 'cargo_type' not in shipment:
                    shipment['cargo_type'] = "NOT PROVIDED"
                if 'customer' not in shipment:
                    shipment['customer'] = "NOT PROVIDED"
                if 'weight_kg' not in shipment:
                    shipment['weight_kg'] = "NOT PROVIDED" 
                found_shipments.append(shipment) 
                found = True #id was found
                break

        if not found: #if id was not matched
            missing_shipments.append(id)
        num_missing_shipments = len(missing_shipments) 


    return found_shipments, num_declared_shipments, num_missing_shipments, missing_shipments

#finally, bring all the data together and manifest it. 
def inspect_vessel_manifest(name, date):
    call_id = find_id_in_port_calls(name, date)

    if call_id == None:
        return
    
    matching_manifest = get_matching_manifests(call_id)
    date = datetime.strptime(date, "%Y-%m-%d").date() #parsing the string into datetime first
    formated_date = datetime.strftime(date, "%d %B %Y") # formating it

    if matching_manifest == None :
        return
    
    resolved_weight = 0
    found_shipments, num_declared_shipments, num_missing_shipments, missing_shipments = get_matching_shipments(matching_manifest)

    #found_index = 0
    #number = 1
    #for id in matching_manifest['shipment_ids']:
    #    for missing_id in missing_shipments:
    #        if missing_id == id:
    #            print(f"{number}. {id} | MISSING RECORD")
    #        else:
    #            break
    #    if found_index <= len(found_shipments)-1:
    #        shipment = found_shipments[found_index]
    #        found_index += 1                                                                                      
    #        resolved_weight += shipment['weight_kg']                                                              
    #        print(f"{number}. {shipment['shipment_id']} | {shipment['customer']} | {shipment['weight_kg']:.1f} kg | {shipment['cargo_type']}")
    #    number += 1

    resolved_weight = 0
    found_index = 0
    number = 1

    for shipment_id in matching_manifest['shipment_ids']:
        if shipment_id in missing_shipments:
            print(f"{number}. {shipment_id} | MISSING RECORD")
        else:
            shipment = found_shipments[found_index]
            found_index += 1
            resolved_weight += shipment['weight_kg']
            print(f"{number}. {shipment_id} | {shipment['customer']} | {shipment['weight_kg']:.1f} kg | {shipment['cargo_type']}")
        number += 1

            
    #found_index = 0
    #number = 1
    #for shipment_id in matching_manifest['shipment_ids']:
    #   print(shipment_id, 'and', missing_shipments, "IF COMPARING THESE TWO")
    #   if shipment_id == missing_id:
    #       print(f"{number}. {shipment_id} | MISSING RECORD")
    #   elif found_index <= len(found_shipments)-1:
    #       print(found_index, "INDEX")
    #       shipment = found_shipments[found_index]
    #       found_index += 1
    #       resolved_weight += shipment['weight_kg']
    #       print(f"{number}. {shipment['customer']} | {shipment['weight_kg']:.1f} kg | {shipment['cargo_type']}")
    #   number += 1

    #i = 1
    #if found_shipment == None:
    #    for mis_ship in missing_shipments:
    #                print(f"{i}. {mis_ship} | MISSING RECORD")
    #                i += 1
    #                resolved_weight = 0
    #else:
    #    for shipment in found_shipment:    
    #                print(f"{i}. {shipment['shipment_id']} | {shipment['customer']} | {shipment['weight_kg']:.1f} kg | {shipment['cargo_type']}")
    #                resolved_weight += shipment['weight_kg']
    #                i += 1     

        
    print(f"Declared shipments: {num_declared_shipments}")
    print(f"Resolved weight: {resolved_weight:.2f} kg")
    print(f"Missing shipment records: {num_missing_shipments}")


def identify_priority_cargo(call_id):
    call_id = call_id.strip().upper()
    matching_manifests = get_matching_manifests(call_id)
    matching_shipment = get_matching_shipments(matching_manifests)


    return

def main(): 
    inspect_vessel_manifest("Baltic Pioneer", "2026-10-01")
    #display_registered_vessels(load_vessels())


    return
if __name__ == "__main__":
    main()
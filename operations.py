"""HarborFlow operational business rules.

Keep calculations and record-processing logic separate from user interaction
where practical.
""" 
import os 
import tempfile
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import data_access
import text_tools

script_dir = os.path.dirname(os.path.abspath(__file__)) #directory the main.py is in. The assumption is the dataset will be in the same directory.

def get_vessel_name(vessel):
    return vessel['name'].lower() #make it case insensitive

def sort_vessels_alphabetically(vessels):
    sorted_vessels = sorted(vessels, key=get_vessel_name) #key expects a function and with each vessel we give a key, name of the vessel
    return sorted_vessels
 

def load_vessels():
    path_vessels = os.path.join(f"{script_dir}/dataset/vessels")
    vessels, vessel_files_skipped = data_access.load_json(path_vessels)

    valid_vessels = []
    for vessel in vessels:
        if isinstance(vessel, dict) and 'vessel_id' in vessel and 'name' in vessel and 'imo' in vessel and 'capacity_teu'in vessel: #makes sure that vessel is a dict and all the required fields are present
            valid_vessels.append(vessel)
        else:
            vessel_files_skipped += 1 #if one of the vessels is missing a key, we add it to the count
    valid_vessels = sort_vessels_alphabetically(valid_vessels)
    
    return valid_vessels, vessel_files_skipped #returns a list of dictionaries of vessels and num of files skipped as a tuple

def display_registered_vessels(): 
    vessels, vessel_files_skipped = load_vessels()
    print("Registered HarborFlow vessels:")
    for v in vessels:
        print(f"- {v['name']} | IMO {v['imo']} | {v['capacity_teu']:,} TEU") 
    print(f"Skipped vessel files: {vessel_files_skipped}")


# finds id in the port call in accordance with the vessels name, then sorts the calls by date and alphabetically if needed. 
def find_id_in_port_calls(vessels_name, reference_date): 
    vessels_name = vessels_name.strip().lower()

    
    filename = os.path.join(script_dir, "dataset", "port_calls.csv")
    vessels, vessel_files_skipped = load_vessels()
    vessel_id = ""
    for v in vessels:
        if vessels_name.lower() == v['name'].lower(): #checks case insensitively since all is lower case
            vessel_id = v['vessel_id'] 
    
    if vessel_id == "":
        print("Vessel not found.")
        return        
    port_calls = data_access.load_csv(filename, vessel_id) #list of calls of a vessel with the given ID    
    
    try:
        reference_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
    except ValueError:
        print("Error - Date must use YYYY-MM-DD.")
        return
    calls_to_sort = [] #list of ids to sort alphabetically if they have the same date  
    for call in port_calls:
        try: #in case of invalid date, put it in try. If one is invalid, just continue
            corrected_date = datetime.strptime(call[3], "%Y-%m-%d").date()
            call[3] = corrected_date
            if call[3] >= reference_date: #
                calls_to_sort.append(call)
        except ValueError:
            continue 
    
    if not calls_to_sort:
        print("No upcoming port calls found.")
        return
    
    port_call = min(calls_to_sort, key=get_port_call_date)
    id_port_call = port_call[0]
    time_port_call = port_call[3]
    return id_port_call, time_port_call

def get_port_call_date(call):
    return (call[3], call[0])

#retrieves the manifests from the dataset and sorts them according with the vessels id.
def get_matching_manifests(port_call_id):
    if port_call_id == None:
            return
    
    calls_id = port_call_id
    manifest_directory = f"{script_dir}/dataset/manifests"
    list_manifests = data_access.load_json(manifest_directory)[0] 

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
    if dict_manifest == None:
        return
    shipment_ids_in_manifest = dict_manifest["shipment_ids"]
    shipment_directory = f"{script_dir}/dataset/shipments"
    list_of_dicts_shipments = data_access.load_json(shipment_directory)[0]

    found_shipments = []
    missing_shipments = []
    num_missing_shipments = 0
    num_declared_shipments = len(shipment_ids_in_manifest) 

    #itterates the ids stated in the manifest
    for id in shipment_ids_in_manifest: 
        found = False #the id was not found 
        for shipment in list_of_dicts_shipments: # for every id, compare the shipments keys. So if id is matching, the shipment should have certain keys
            if id == shipment["shipment_id"]: 
                #check if every key is in the shipment dict. If it is not, add it and give it a string "NOT PROVIDED" or False where appropriate
                
                if 'hazardous' not in shipment:
                    shipment['hazardous'] = False
                if 'temperature_controlled' not in shipment:
                    shipment['temperature_controlled'] = False
                if 'cargo_type' not in shipment:
                    shipment['cargo_type'] = "NOT PROVIDED" 
                found_shipments.append(shipment) 
                found = True #id was found
                break

        if not found: #if id was not matched
            missing_shipments.append(id)
        num_missing_shipments = len(missing_shipments)  
    return found_shipments, num_declared_shipments, num_missing_shipments, missing_shipments
 

#finally, bring all the data together and manifest it. 
def inspect_vessel_manifest(name, date):
    name = name.strip()

    #eventhough both functions have checks for none reurn, the program still need to return in the caller function
    result = find_id_in_port_calls(name, date)
    if result == None:
        return
    call_id, call_time = result
    matching_manifest = get_matching_manifests(call_id)
    if matching_manifest == None:
        return
    
    formated_date = datetime.strftime(call_time, "%d %B %Y") # formating the date to display in (dd month yyyy) format

    found_shipments, num_declared_shipments, num_missing_shipments, missing_shipments = get_matching_shipments(matching_manifest)
    if found_shipments == None or num_declared_shipments == None or num_missing_shipments == None or missing_shipments == None:
        return


    print(f"Manifest for {name.title()} | Call {call_id} | {formated_date}")
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
            print(f"{number}. {shipment_id} | {shipment['customer']} | {shipment['weight_kg']} kg | {shipment['cargo_type']}")
        number += 1 

    print(f"Declared shipments: {num_declared_shipments}")
    print(f"Resolved weight: {resolved_weight:.2f} kg")
    print(f"Missing shipment records: {num_missing_shipments}")

# check if the given call id exists in port calls csv
def check_for_presence(call_id):
    found = False
    filename = os.path.join(script_dir, "dataset", "port_calls.csv")
    with open(filename,"r") as file:
           reader = data_access.csv.reader(file)
           rows = list(reader) 

    for call in rows: 
        if call[0] == call_id:
            found = True
    return found

def identify_priority_cargo(call_id):
    call_id = call_id.strip().upper() #upper makes sure that users input is always in upper case. Therefore it always compares the upper to upper (call id in the csb is upper). 
    if not check_for_presence(call_id):
        print("Port call not found.")
        return

    matching_manifests = get_matching_manifests(call_id)
    if matching_manifests == None: 
        return

    if get_matching_shipments(matching_manifests)[0] == None:
        return

    found_shipments = get_matching_shipments(matching_manifests)[0]

    list_controlled = []
    list_cold_chain = []
    list_expedite = []
    list_standart = []

    for shipment in found_shipments:
        if shipment['hazardous'] == True:
            print(f"{shipment['shipment_id']} | CONTROLLED | hazardous cargo")
            list_controlled.append(shipment['shipment_id'])
        elif shipment['temperature_controlled'] == True:
            print(f"{shipment['shipment_id']} | COLD CHAIN | temperature is controlled")
            list_cold_chain.append(shipment['shipment_id'])
        elif shipment['priority'] == "EXPRESS":
            print(f"{shipment['shipment_id']} | EXPEDITE | express service")
            list_expedite.append(shipment['shipment_id'])
        elif shipment['weight_kg'] >= 5000:
            print(f"{shipment['shipment_id']} | EXPEDITE | weight is or above 5000kg")
            list_expedite.append(shipment['shipment_id'])
        else:
            print(f"{shipment['shipment_id']} | STANDARD | none of other criteria apply")
            list_standart.append(shipment['shipment_id'])

    print(f"Category totals: CONTROLLED={len(list_controlled)}, COLD CHAIN={len(list_cold_chain)}, EXPEDITE={len(list_expedite)}, STANDARD={len(list_standart)}")
    return

if __name__ == "__main__":
    main() 
    pass
 

import csv
from data_access import EXPORTS_FOLDER, read_json_files, read_json_records, read_portcalls

PROFILE_HEADER = ['customer', 'shipment_count', 'total_weight_kg',
                  'express_count', 'destinations']

MONTH_NAMES = ('', 'January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December')


def customer_search():
    customer = input('Customer name: ').strip()
    try:
        profile = summarize_customer(read_json_files(), customer)
        if profile is None:
            print('Customer not found.')
            return
        save_customer_profile(profile)
    except (OSError, ValueError, csv.Error) as error:
        print(f'Could not update customer profile: {error}')
        return
    print('Customer profile updated: exports/customer-profiles.csv')


def port_calls_by_month():
    while True:
        try:
            month = int(input('Month (1-12): '))
            if 1 <= month <= 12:
                break
        except ValueError:
            pass
        print('Error - Enter a month from 1 to 12.')
    try:
        calls = find_portcalls(read_portcalls(), read_json_records('vessels'), month)
    except (OSError, csv.Error) as error:
        print(f'Could not read port calls: {error}')
        return
    if not calls:
        print('No port calls found.')
        return
    print(f'Port calls in {MONTH_NAMES[month]}:')
    for arrival, vessel_name, call in calls:
        formatted_date = f'{arrival.day:02d} {MONTH_NAMES[arrival.month]} {arrival.year}'
        print(f"- {formatted_date} | {vessel_name} | {call['port_code']} | {call['call_id']}")

def sanitize_incident_service():
    incidents, skipped = data_access.load_incidents()
    incidents.sort(key=lambda incident: incident["title"].lower())

    if not incidents:
        print("No incident reports found.")
        return

    for number, incident in enumerate(incidents, 1):
        print(f"{number}. {incident['title']}")

    selected = None
    choosing=True
    while choosing:
        raw = input("Select incident: ").strip()
        try:
            number = int(raw)
        except ValueError:
            number = 0
        if 1 <= number <= len(incidents):
            selected = incidents[number - 1]
            choosing=False
        else:
            print("Error - Select a listed incident.")

    cleaned, changed = text_tools.sanitize_report(selected["report"])
    if not changed:
        print("Incident contains no share-sensitive identifiers.")
        return

    data_access.save_sanitized_report(selected["incident_id"], cleaned)
    print("Incident sanitized")


def sequence_service():
    call_id = input("Call ID: ").strip()

    if not data_access.port_call_exists(call_id):
        print("Port call not found")
        return

    manifest = data_access.load_manifest_by_call_id(call_id)
    if manifest is None:
        print("Manifest unavailable")
        return

    events = [str(code) for code in manifest["event_codes"]]
    length, sequence = text_tools.longest_unique_sequence(events)

    print("Event codes: " + ",".join(events))
    print(f"Longest stable sequence length: {length}")
    print("Sequence: " + " -> ".join(sequence))


def summarize_customer(shipments, customer):
    matches = []
    for shipment in shipments:
        try:
            name = shipment['customer'].strip()
            weight = Decimal(str(shipment['weight_kg']))
            destination = shipment['destination'].strip()
            priority = shipment['priority'].strip().upper()
            if not name or not destination or not weight.is_finite() or weight < 0:
                raise ValueError('invalid shipment fields')
        except (KeyError, AttributeError, ValueError, InvalidOperation, TypeError):
            print(f"Skipping invalid shipment: {shipment.get('shipment_id', 'unknown')}.")
            continue
        if name.casefold() == customer.strip().casefold():
            matches.append((name, weight, destination, priority))
    if not matches:
        return None
    return {
        'customer': matches[0][0],
        'shipment_count': len(matches),
        'total_weight_kg': f"{sum((item[1] for item in matches), Decimal('0')):.2f}",
        'express_count': sum(item[3] == 'EXPRESS' for item in matches),
        'destinations': '|'.join(sorted({item[2] for item in matches})),
    }


def save_customer_profile(profile):
    path = EXPORTS_FOLDER / 'customer-profiles.csv'
    rows = []
    if path.exists():
        with path.open(encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)
            if reader.fieldnames != PROFILE_HEADER:
                raise ValueError('Unexpected customer profile CSV header')
            rows = list(reader)
    updated = []
    replaced = False
    for row in rows:
        if row['customer'].strip().casefold() == profile['customer'].casefold():
            if not replaced:
                updated.append(profile)
                replaced = True
        else:
            updated.append(row)
    if not replaced:
        updated.append(profile)
    EXPORTS_FOLDER.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='', dir=EXPORTS_FOLDER,
                                         prefix='customer-profiles-', suffix='.tmp', delete=False) as file:
            temporary_path = file.name
            writer = csv.DictWriter(file, fieldnames=PROFILE_HEADER)
            writer.writeheader()
            writer.writerows(updated)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and os.path.exists(temporary_path):
            os.unlink(temporary_path)


def find_portcalls(calls, vessels, month):
    names = {}
    for vessel in vessels:
        if isinstance(vessel.get('vessel_id'), str) and isinstance(vessel.get('name'), str):
            names[vessel['vessel_id']] = vessel['name']
        else:
            print('Skipping invalid vessel record.')
    matches = []
    for call in calls:
        try:
            arrival = date.fromisoformat(call.get('arrival_date', ''))
        except (ValueError, TypeError):
            print(f"Skipping {call.get('call_id', 'unknown')}: invalid date {call.get('arrival_date')}.")
            continue
        vessel_id = call.get('vessel_id')
        if vessel_id not in names:
            print(f"Skipping {call.get('call_id', 'unknown')}: unknown vessel_id {vessel_id}.")
            continue
        if arrival.month == month:
            matches.append((arrival, names[vessel_id], call))
    return sorted(matches, key=lambda item: (item[0], item[1]))

import json
import os


def load_json(directory):
    print(directory)
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

def get_vessel_name(vessel):
    return vessel['name']

def sort_vessels_by_name(vessels):
    sorted_vessels = sorted(vessels, key=get_vessel_name)
    return sorted_vessels


def load_vessels():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path_vessels = os.path.join(f"{script_dir}/dataset/vessels")


    data = load_json(path_vessels)  
    data = sort_vessels_by_name(data)

    i = 0
    for d in data:
        print(f"- {d['name']} | IMO {d['imo']} | {d['capacity_teu']} TEU")
        i += 1


def main():

    load_vessels()
    

if __name__ == "__main__":
    main()
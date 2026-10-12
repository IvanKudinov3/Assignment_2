import json
from pathlib import Path



def json_reader(file_path):
    print(file_path)
    damaged_files = 0
    list_of_dicts = []
    for file in file_path.glob("*.json"): 
        with open(file, "r") as f:
            try:
                data = json.load(f)  
                list_of_dicts.append(data)
            except json.JSONDecodeError as e:
                damaged_files += 1
                print(f"Error decoding JSON from file {file}: {e}")
                print(f"Total damaged files: {damaged_files}")
    return list_of_dicts

def print_vessel_data():
    script_dir = Path(__file__).parent
    path_vessels = Path(f"{script_dir}/dataset/vessels")
    data = json_reader(path_vessels)
    i = 0
    for d in data: 
        print(f"- {d['name']} | IMO {d['imo']} | {d['capacity_teu']} TEU")
        i += 1


def main():
    print_vessel_data()
    

if __name__ == "__main__":
    main()
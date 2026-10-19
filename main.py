import HarborFlow_Intelegence_Console
import operations
def menu():
    print("HARBORFLOW PORT INTELLIGENCE \n"
    "1. List registered vessels\n"
    "2. Inspect a vessel manifest\n"
    "3. Identify priority cargo\n"
    "4. Export a customer operations profile\n"
    "5. Find port calls by month\n"
    "6. Sanitize an incident report\n"
    "7. Analyze the longest stable event sequence\n"
    "8. Assess weather risk for upcoming calls\n"
    "9. Search incident reports\n"
    "10. Close console\n")
    user_input = input("Select service: ") 
    return user_input


def main(): 
    while True:
        match menu(): 
            case "1":  
                operations.display_registered_vessels()
                print()
            case "2":
                operations.inspect_vessel_manifest(input("Type in the name of the vessel: "), input("Type in the date: "))
                print()
            case "3":
                operations.identify_priority_cargo(input("Type in the port call ID: "))
                print()
            case "4":
                 customer_search()
                 print()
            case "5":
                port_calls_by_month()
                print()
            case "6":
                operations.sanitize_incident_service()
                print()
            case "7":
                operations.sequence_service()
                print()
            case "8":
                print("Assessing weather risk for upcoming calls...")
                print()
            case "9":
                print("Searching incident reports...")
                print()
            case "10":
                print("Closing console...")
                print()
                exit()
                break
            case _:
                print("Invalid option. Please try again.") 
                print()
        

if __name__ == "__main__":
    main() 
    pass
 

import csv
from data_access import read_json_files, read_json_records, read_portcalls
from operations import find_portcalls, save_customer_profile, summarize_customer

MONTH_NAMES = ('', 'January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December')


def choice_4():
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


def choice_5():
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

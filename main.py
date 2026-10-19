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


if __name__ == "__main__":
    main()

import os
import json
import csv

#Task 4
def customer_search():

    folder = r"C:\Users\toste\Documents\Harborflow\Harborflow data\dataset\shipments"

    while True:

        customer_name = input("Customer name: ").strip()

        shipment_count = 0
        total_weight = 0
        express_count = 0
        destinations = []
        correct_name = ""

        # Search through all JSON files
        for filename in os.listdir(folder):

            if filename.lower().endswith(".json"):

                file_path = os.path.join(folder, filename)

                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)

                if isinstance(data, dict):
                    shipments = data.get("shipments", [data])

                elif isinstance(data, list):
                    shipments = data

                else:
                    shipments = []

                for shipment in shipments:

                    if not isinstance(shipment, dict):
                        continue

                    customer = shipment.get("customer", "").strip()

                    if customer.lower() == customer_name.lower():

                        if correct_name == "":
                            correct_name = customer

                        shipment_count += 1
                        total_weight += float(shipment.get("weight_kg", 0))

                        if shipment.get("priority", "").strip().upper() == "EXPRESS":
                            express_count += 1

                        destination = shipment.get("destination", "").strip().upper()

                        if destination and destination not in destinations:
                            destinations.append(destination)

        # If customer not found, ask again
        if shipment_count == 0:
            print("Customer not found.")
            continue

        # Customer found, leave the search loop
        break

    # Sort destinations alphabetically
    destinations.sort()
    destination_text = "|".join(destinations)

    # Store customer summary in memory
    new_row = [
        correct_name,
        shipment_count,
        f"{total_weight:.2f}",
        express_count,
        destination_text
    ]

    header = [
        "customer",
        "shipment_count",
        "total_weight_kg",
        "express_count",
        "destinations"
    ]

    # Print customer summary
    print()
    print(",".join(header))
    print(",".join(str(value) for value in new_row))

    # Ask if the user wants to export
    while True:
        save = input("\nSave customer profile? (yes/no): ").strip().upper()

        if save == "YES":
            break

        elif save == "NO":
            print("Customer profile not saved.")
            return

        else:
            print("Please enter yes or no.")

    # Choose where to export the CSV
    export_path = os.path.join(
        os.path.dirname(folder),
        "exports",
        "customer-profiles.csv"
    )

    # Store existing customer profiles in memory
    customer_details = []
    found = False

    if os.path.isfile(export_path):

        with open(export_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)

            for row in reader:

                if row and row[0].strip().lower() == correct_name.lower():

                    if not found:
                        customer_details.append(new_row)
                        found = True

                else:
                    customer_details.append(row)

    # Add the customer if not already saved
    if not found:
        customer_details.append(new_row)

    # Create export folder if necessary
    os.makedirs(os.path.dirname(export_path), exist_ok=True)

    # Write to temporary file first
    temp_path = export_path + ".tmp"

    with open(temp_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(customer_details)

    # Safely replace existing file
    os.replace(temp_path, export_path)

    print("Customer profile updated:", export_path)

    # Keep the rest of your code here
    # Sort destinations and join with |

import os
import json
import csv
from datetime import datetime


# Task 5
def port_calls_by_month():

    folder = r"C:\Users\toste\Documents\Harborflow\Harborflow data\dataset"

    # Ask for a valid month
    while True:

        month = input("Month (1-12): ").strip()

        if not month.isdigit():
            print("Error - Enter a month from 1 to 12.")
            continue

        month = int(month)

        if month < 1 or month > 12:
            print("Error - Enter a month from 1 to 12.")
            continue

        break

    month_name = datetime(2026, month, 1).strftime("%B")

    # Read vessel JSON files

     # Read vessel JSON files
    vessel_folder = os.path.join(folder, "vessels")

    vessels = []

    for filename in os.listdir(vessel_folder):

        if filename.lower().endswith(".json"):

            file_path = os.path.join(vessel_folder, filename)

            print("Reading vessel file:", filename)

            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    vessel = json.load(file)

            except json.JSONDecodeError:
                print("Invalid JSON file:", filename)
                continue

            if isinstance(vessel, dict):

                vessel_id = vessel.get("vessel_id", "")
                vessel_name = vessel.get("name", "")

                vessels.append([vessel_id, vessel_name])

    # Read port calls CSV
    file_path = os.path.join(folder, "port_calls.csv")

    port_calls = []

    with open(file_path, "r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:

            # Check arrival date
            try:
                arrival_date = datetime.strptime(
                    row["arrival_date"].strip(), "%Y-%m-%d"
                )

            except (ValueError, TypeError, AttributeError):
                print("Invalid date:", row.get("arrival_date"))
                continue

            # Only include selected month
            if arrival_date.month != month:
                continue

            # Find matching vessel
            vessel_id = row["vessel_id"].strip()
            vessel_name = ""

            for vessel in vessels:

                if vessel[0] == vessel_id:
                    vessel_name = vessel[1]
                    break

            # Skip unknown vessels
            if vessel_name == "":
                print("Unknown vessel_id:", vessel_id)
                continue

            # Store matching port call
            port_calls.append([
                arrival_date,
                vessel_name,
                row["port_code"],
                row["booking_reference"]
            ])

    # Sort by date and vessel name
    port_calls.sort()

    # Print results
    if len(port_calls) == 0:
        print("No port calls found.")
        return

    print(f"\nPort calls in {month_name}:")

    for arrival_date, vessel_name, port_code, booking_reference in port_calls:

        print(
            f"- {arrival_date.strftime('%d %B %Y')} | "
            f"{vessel_name} | "
            f"{port_code} | "
            f"{booking_reference}"
        )

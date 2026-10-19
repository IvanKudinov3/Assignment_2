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
                 operations.customer_search()
                 print()
            case "5":
                operations.port_calls_by_month()
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

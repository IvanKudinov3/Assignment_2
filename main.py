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
                print("Listing registered vessels...")
                print()
            case "2":
                print("Inspecting vessel manifest...")
                print()
            case "3":
                print("Identifying priority cargo...")
                print()
            case "4":
                print("Exporting customer operations profile...")
                print()
            case "5":
                print("Finding port calls by month...")
                print()
            case "6":
                print("Sanitizing incident report...")
                print()
            case "7":
                print("Analyzing longest stable event sequence...")
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

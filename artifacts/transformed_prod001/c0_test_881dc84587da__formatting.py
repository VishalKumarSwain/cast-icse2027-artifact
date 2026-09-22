def run_script():
    while True:
        choice = input("Do you want to string bows or make them (u)? ").strip().lower()
        if choice == "string":
            return "stringing script"
        elif choice == "make":
            return "fletching script"
        elif choice == "u":
            return "reset"
        else:
            print("Invalid choice. Please try again.")

def run_script():
    while True:
        choice_renamed = input("Do you want to string bows or make them (u)? ").strip().lower()
        if choice_renamed == 'string':
            return "stringing script"
        elif choice_renamed == 'make':
            return "fletching script"
        elif choice_renamed == 'u':
            return "reset"
        else:
            print("Invalid choice. Please try again.")

import re
import sys
# Import the classes/functions from our other files
from blockchain import Blockchain
from hasher import hash_data

"""
File: main.py
Description: Serves as the main driver for the console application.
It handles user input and orchestrates the registration and
verification processes by interacting with the Blockchain and Hasher.
"""

def validate_id_number(id_number):
    """
    Validates the identity number (e.g., Aadhaar).
    --- COMPLETES CHALLENGE: Input Validation ---
    A basic check: must be exactly 12 digits, no letters or symbols.
    
    Args:
        id_number (str): The input string from the user.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    # Regex pattern: ^ means start, \d{12} means exactly 12 digits, $ means end.
    pattern = re.compile(r"^\d{12}$")
    
    if pattern.match(id_number):
        return True
    else:
        print("\nError: Invalid Identity Number.")
        print("Input must be exactly 12 digits (e.g., 123456789012).")
        return False

def print_menu():
    """
    Helper function to display the main menu to the user.
    """
    print("\n" + "="*40)
    print("   Identity Verification System Menu   ")
    print("="*40)
    print("1. Register New Identity (e.g., Aadhaar)")
    print("2. Verify Identity")
    print("3. Check Blockchain Integrity")
    print("4. Print Entire Blockchain (Admin/Debug)")
    print("5. Exit")
    print("="*40)

def main():
    """
    Main driver function for the console application.
    """
    
    # 1. Initialize the blockchain.
    # This automatically calls blockchain.load_chain()
    # to load 'blockchain.json' if it exists.
    try:
        my_blockchain = Blockchain()
    except Exception as e:
        print("\n" + "!"*50)
        print("   A CRITICAL ERROR OCCURRED ON STARTUP   ")
        print(f"   Error: {e}")
        print("   Could not load or create 'blockchain.json'.")
        print("   Please check file permissions and try again.")
        print("!"*50)
        sys.exit() # Exit if blockchain can't be loaded

    
    print("\nWelcome to the Decentralized Identity Verification System.")
    print("Blockchain is loaded and ready.")

    # 2. Start the main application loop
    while True:
        print_menu()
        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            # --- 1. Register New Identity ---
            id_number = input("Enter the 12-digit Identity Number to register: ").strip()
            
            # --- Input Validation (from report challenge) ---
            if validate_id_number(id_number):
                # Hash the data before storing it
                id_hash = hash_data(id_number)
                if id_hash:
                    print(f"Hashed ID: {id_hash}")
                    # Add the hash to the blockchain
                    # The add_block method handles duplicate checks
                    my_blockchain.add_block(id_hash)
        
        elif choice == '2':
            # --- 2. Verify Identity ---
            id_number = input("Enter the 12-digit Identity Number to verify: ").strip()
            
            if validate_id_number(id_number):
                # Hash the input data to check against the chain
                id_hash = hash_data(id_number)
                if id_hash:
                    print(f"Checking for hash: {id_hash}")
                    
                    # Check if the hash exists in the chain
                    if my_blockchain.verify_identity(id_hash):
                        print("\n*")
                        print("*** VERIFICATION SUCCESSFUL ***")
                        print("This identity is registered on the blockchain.")
                        print("*")
                    else:
                        print("\n*")
                        print("*** VERIFICATION FAILED ***")
                        print("This identity was not found.")
                        print("*")
        
        elif choice == '3':
            # --- 3. Validate Blockchain Integrity ---
            print("\nRunning blockchain integrity check...")
            my_blockchain.is_chain_valid()
        
        elif choice == '4':
            # --- 4. Print Blockchain ---
            print("\nDisplaying all blocks in the chain...")
            my_blockchain.print_chain()

        elif choice == '5':
            # --- 5. Exit ---
            print("Exiting system. Goodbye.")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

# Standard Python entry point
# We use .strip() on _name_ to fix a rare environment issue
# where it might be reported as ' _main_' with a leading space.
if __name__.strip() == "__main__":
    main()
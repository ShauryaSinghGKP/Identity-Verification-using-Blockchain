import hashlib
import json
from datetime import datetime
from hasher import hash_data # Import our simple hash function

"""
File: blockchain.py
Description: Defines the Block and Blockchain classes. This is the core
engine of the identity system. It handles block creation, validation,
and persistent storage.
"""

class Blockchain:
    """
    Manages the chain of blocks, including adding new blocks
    and validating the integrity of the chain.
    """
    
    def __init__(self):
        """
        Constructor for the Blockchain.
        """
        # --- This is the main list that holds all the blocks ---
        # The error was caused by using "self.chain" instead of "self.blockchain"
        self.blockchain = []
        self.storage_file = "blockchain.json"
        
        # --- COMPLETES PENDING TASK: Persistent Storage ---
        # Try to load the chain from the file on startup.
        # If no file exists, create the Genesis Block.
        self.load_chain()

    def new_block(self, data, previous_hash):
        """
        Creates a new block to be added to the chain.
        
        Args:
            data (str): The data to be stored (e.g., hashed Aadhaar).
            previous_hash (str): The hash of the previous block in the chain.
            
        Returns:
            dict: A new block object.
        """
        block = {
            'index': len(self.blockchain) + 1,
            'timestamp': str(datetime.now()),
            'data': data,
            'previous_hash': previous_hash,
            'hash': None # The hash will be calculated next
        }
        
        # Calculate the hash for this new block
        block['hash'] = self.calculate_block_hash(block)
        return block

    def get_last_block(self):
        """
        Returns the last block in the chain.
        """
        return self.blockchain[-1]

    def calculate_block_hash(self, block):
        """
        Calculates the SHA-256 hash of a given block.
        
        Args:
            block (dict): The block to hash.
            
        Returns:
            str: The calculated hash.
        """
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes
        
        # Create a copy to avoid modifying the original block
        block_to_hash = block.copy()
        # Set hash to None for calculation, just like in new_block
        block_to_hash['hash'] = None 
        
        block_string = json.dumps(block_to_hash, sort_keys=True).encode()
        return hash_data(block_string.decode()) # Use our hasher utility

    def create_genesis_block(self):
        """
        Creates the first block in the chain (Genesis Block).
        """
        genesis_block = self.new_block(
            data="Genesis Block",
            previous_hash="0"
        )
        self.blockchain = [genesis_block]
        self.save_chain()

    def add_block(self, new_data_hash):
        """
        Adds a new block to the chain.
        """
        # --- Duplicate Check (from report's pending tasks) ---
        if self.verify_identity(new_data_hash):
            print("\nError: This identity is already registered.")
            return
        
        try:
            # Get the previous block and its hash
            last_block = self.get_last_block()
            previous_hash = last_block['hash']
            
            # Create the new block
            new_block = self.new_block(new_data_hash, previous_hash)
            
            # Add it to the chain and save
            self.blockchain.append(new_block)
            self.save_chain()
            
            print(f"\nSuccess: Block #{new_block['index']} (Identity: {new_data_hash[:10]}...) added to the chain.")
            
        except Exception as e:
            print(f"\nError adding block: {e}")

    def is_chain_valid(self):
        """
        Checks the integrity of the entire blockchain.
        1. Checks if each block's stored hash matches its calculated hash.
        2. Checks if each block's 'previous_hash' matches the hash
           of the actual previous block.
           
        Returns:
            bool: True if valid, False otherwise.
        """
        for i in range(1, len(self.blockchain)):
            current_block = self.blockchain[i]
            previous_block = self.blockchain[i-1]

            # 1. Check if the block's hash is correct
            # We re-calculate the hash from the block's content
            recalculated_hash = self.calculate_block_hash(current_block)

            if current_block['hash'] != recalculated_hash:
                print(f"\nIntegrity FAILED: Block #{current_block['index']} hash is invalid.")
                print(f"Stored:   {current_block['hash']}")
                print(f"Recalc'd: {recalculated_hash}")
                return False

            # 2. Check if the previous_hash link is correct
            if current_block['previous_hash'] != previous_block['hash']:
                print(f"\nIntegrity FAILED: Block #{current_block['index']} 'previous_hash' does not match Block #{previous_block['index']} 'hash'.")
                return False

        print("\nBlockchain Integrity Check: PASS")
        print("All blocks are valid and chain is secure.")
        return True

    def verify_identity(self, identity_hash):
        """
        Checks if a given hash already exists in the blockchain.
        --- COMPLETES PENDING TASK: Duplicate Entry Prevention ---
        
        Args:
            identity_hash (str): The hash to check for.
            
        Returns:
            bool: True if hash exists, False otherwise.
        """
        # Start from 1 to skip the Genesis Block
        # --- FIX was here: Use self.blockchain, not self.chain ---
        for block in self.blockchain[1:]:
            if block['data'] == identity_hash:
                return True
        return False

    def print_chain(self):
        """
        Helper function to print the entire blockchain to the console.
        """
        if not self.blockchain:
            print("The blockchain is empty.")
            return
            
        for block in self.blockchain:
            print(f"\nBlock {block['index']} " + "-"*30)
            print(f"  Timestamp:     {block['timestamp']}")
            print(f"  Data:          {block['data']}")
            print(f"  Previous Hash: {block['previous_hash']}")
            print(f"  Hash:          {block['hash']}")
            print("-"*38)
            
    # --- Persistence Functions ---

    def save_chain(self):
        """
        Saves the entire blockchain to the JSON file.
        """
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.blockchain, f, indent=4)
        except Exception as e:
            print(f"\nCRITICAL: Failed to save blockchain to {self.storage_file}: {e}")

    def load_chain(self):
        """
        Loads the blockchain from the JSON file.
        If no file exists, it creates a new chain with a Genesis Block.
        """
        try:
            with open(self.storage_file, 'r') as f:
                self.blockchain = json.load(f)
                if not self.blockchain:
                    print("Blockchain file is empty. Creating Genesis Block.")
                    self.create_genesis_block()
                else:
                    print(f"Blockchain with {len(self.blockchain)} blocks loaded from {self.storage_file}.")
        except FileNotFoundError:
            print(f"No file found at {self.storage_file}. Creating new blockchain with Genesis Block.")
            self.create_genesis_block()
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.storage_file}. File might be corrupt.")
            print("Creating new blockchain with Genesis Block.")
            self.create_genesis_block()
        except Exception as e:
            print(f"An unexpected error occurred during loading: {e}")
            self.create_genesis_block()


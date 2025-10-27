import hashlib
import sys

"""
File: hasher.py
Description: As per the project report, this is a utility module dedicated
to handling the SHA-256 hashing function. It keeps the hashing logic
separate from the main application logic.
"""

def hash_data(data_string):
    """
    Hashes a given string using the SHA-256 algorithm.
    
    The report specifies SHA-256 to convert identity data (like Aadhaar)
    into a secure, fixed-length cryptographic digest.

    Args:
        data_string (str): The input string to be hashed (e.g., "123456789012").

    Returns:
        str: The resulting SHA-256 hash as a hexadecimal string.
    """
    try:
        # 1. Encode the string into bytes
        #    The hashlib functions require byte-like objects, not strings.
        #    'utf-8' is a standard encoding.
        data_bytes = data_string.encode('utf-8')
        
        # 2. Create a new SHA-256 hash object
        sha256_hash = hashlib.sha256(data_bytes)
        
        # 3. Get the hexadecimal representation of the hash digest
        return sha256_hash.hexdigest()
        
    except Exception as e:
        print(f"Error during hashing: {e}", file=sys.stderr)
        return None
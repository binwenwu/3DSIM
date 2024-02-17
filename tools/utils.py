import mmh3

def generate_short_hash(input_string, length=8):
    # Calculate MurmurHash
    hash_value = mmh3.hash(input_string)
    
    # Convert the hash value to a string and take the first 'length' characters
    hash_str = str(hash_value)
    short_hash = hash_str[:length]
    return short_hash

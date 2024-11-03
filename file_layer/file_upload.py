from .encryption import encrypt_data
from .redundancy import encode_file, encode_shard
from .sharding import split_data
from .metadata import create_shard_mapping
from .config import DEFAULT_SHARD_SIZE
import math

def Distribute(file_obj, private_key, num_shards=None):
    # Read file data
    file_data = file_obj.read()
    file_size = len(file_data)

    # File-level Reed-Solomon encoding
    encoded_file_data = encode_file(file_data)

    # Calculate shard size based on number of shards
    shard_size = len(encoded_file_data) // num_shards if num_shards else DEFAULT_SHARD_SIZE
    
    # Split file data into shards
    shards = split_data(encoded_file_data, shard_size)
    
    # Shard-level Reed-Solomon encoding for each shard
    encoded_shards = [encode_shard(shard) for shard in shards]
    
    # Encrypt each shard and create hash mapping
    encrypted_shards = [encrypt_data(shard, private_key) for shard in encoded_shards]
    shard_mapping = create_shard_mapping(encrypted_shards)
    
    return encrypted_shards, shard_mapping

def split_data(data, shard_size):
    """Split data into chunks of shard_size."""
    return [data[i:i + shard_size] for i in range(0, len(data), shard_size)]

def merge_data(shards):
    """Combine shards to form the original data."""
    return b''.join(shards)

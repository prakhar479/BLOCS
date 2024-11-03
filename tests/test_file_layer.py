# tests/test_sharding.py
import io
import pytest
from file_layer import Distribute, Assimilate
from Crypto.PublicKey import RSA

@pytest.fixture(scope="module")
def rsa_key():
    # Generate RSA key pair for testing
    key = RSA.generate(2048)
    return key.export_key()

def test_distribute_and_assimilate(rsa_key):
    # Sample file data
    test_data = b"Sample test data for sharding and encoding."
    
    # Create file object and distribute it
    file_obj = io.BytesIO(test_data)
    shards, mapping = Distribute(file_obj, rsa_key)
    
    # Check that shards were created
    assert len(shards) > 0
    
    # Reassemble and verify integrity of the data
    reconstructed_data = Assimilate(shards, mapping, rsa_key)
    assert reconstructed_data == test_data

if __name__ == "__main__":
    pytest.main(["-v", "test_file_layer.py"])
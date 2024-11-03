# tests/test_sharding.py
import unittest
import io
from file_layer import Distribute, Assimilate
from Crypto.PublicKey import RSA

class TestFileSharding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate RSA key pair for testing
        key = RSA.generate(2048)
        cls.private_key = key.export_key()

    def test_distribute_and_assimilate(self):
        # Sample file data
        test_data = b"Sample test data for sharding and encoding."
        
        # Create file object and distribute it
        file_obj = io.BytesIO(test_data)
        shards, mapping = Distribute(file_obj, self.private_key)
        
        # Check that shards were created
        self.assertGreater(len(shards), 0)
        
        # Reassemble and verify integrity of the data
        reconstructed_data = Assimilate(shards, mapping, self.private_key, shard_parity=2)
        self.assertEqual(reconstructed_data, test_data)

if __name__ == '__main__':
    unittest.main()

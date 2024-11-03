import argparse
from file_layer.file_upload import Distribute
from file_layer.file_retrieval import Assimilate
from network_layer.node import Node
import os
import pickle
import uuid

# Constants for file operations
UPLOADS_DB = "uploads.db"

class Client:
    def __init__(self, node_id, host, port, bootstrap_address=None):
        self.node = Node(node_id, host, port, bootstrap_address)
        self.uploaded_files = self.load_uploaded_files()

    def load_uploaded_files(self):
        if os.path.exists(UPLOADS_DB):
            with open(UPLOADS_DB, 'rb') as f:
                return pickle.load(f)
        return {}

    def save_uploaded_files(self):
        with open(UPLOADS_DB, 'wb') as f:
            pickle.dump(self.uploaded_files, f)

    def upload_file(self, file_path, private_key):
        try:
            with open(file_path, 'rb') as file_obj:
                file_id = str(uuid.uuid4())
                encrypted_shards, shard_mapping = Distribute(file_obj, private_key, num_shards=5)
                # Broadcasting to network peers for storage
                self.node.broadcast_data({"type": "store", "file_id": file_id, "shards": encrypted_shards, "mapping": shard_mapping})
                self.uploaded_files[file_id] = (file_path, shard_mapping)
                self.save_uploaded_files()
                print(f"File '{file_path}' uploaded successfully. File ID: {file_id}")
        except Exception as e:
            print(f"Failed to upload file: {e}")

    def retrieve_file(self, file_id, output_path, private_key):
        if file_id not in self.uploaded_files:
            print(f"File ID '{file_id}' not found.")
            return

        try:
            _, shard_mapping = self.uploaded_files[file_id]
            # Retrieve shards from network
            shards = self.node.get_data(file_id)
            original_data = Assimilate(shards, shard_mapping, private_key)
            with open(output_path, 'wb') as output_file:
                output_file.write(original_data)
            print(f"File retrieved successfully as '{output_path}'")
        except Exception as e:
            print(f"Failed to retrieve file: {e}")

    def list_files(self):
        if not self.uploaded_files:
            print("No files uploaded.")
            return
        for file_id, (path, _) in self.uploaded_files.items():
            print(f"File ID: {file_id}, Original Path: {path}")

    def start(self):
        self.node.start_node()

    def stop(self):
        self.node.shutdown()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P2P Client for File Sharing")
    parser.add_argument("operation", choices=["upload", "retrieve", "list"], help="Operation to perform")
    parser.add_argument("--file", help="Path to the file for upload or retrieval")
    parser.add_argument("--file_id", help="File ID for retrieval")
    parser.add_argument("--output", help="Output path for retrieved file")
    parser.add_argument("--key", required=True, help="Private key for encryption/decryption")
    parser.add_argument("--host", default="localhost", help="Host address of the client node")
    parser.add_argument("--port", type=int, default=8001, help="Port of the client node")
    parser.add_argument("--bootstrap", help="Bootstrap node address in the format 'host:port'")

    args = parser.parse_args()
    bootstrap = tuple(args.bootstrap.split(":")) if args.bootstrap else None
    client = Client(node_id=2, host=args.host, port=args.port, bootstrap_address=bootstrap)

    client.start()
    if args.operation == "upload" and args.file:
        client.upload_file(args.file, args.key.encode())
    elif args.operation == "retrieve" and args.file_id and args.output:
        client.retrieve_file(args.file_id, args.output, args.key.encode())
    elif args.operation == "list":
        client.list_files()
    else:
        print("Invalid arguments provided.")
    client.stop()

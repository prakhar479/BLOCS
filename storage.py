import argparse
from network_layer.node import Node

class StorageNode:
    def __init__(self, node_id, host, port, bootstrap_address=None):
        self.node = Node(node_id, host, port, bootstrap_address)
        self.stored_files = {}

    def handle_store_request(self, file_id, shards):
        print(f"Received storage request for file ID: {file_id}")
        accept = input("Do you want to accept this storage request? (y/n): ").strip().lower()
        if accept == 'y':
            self.stored_files[file_id] = shards
            print(f"File ID '{file_id}' stored successfully.")
        else:
            print(f"Storage request for file ID '{file_id}' rejected.")
            self.node.send_data(peer, {"type": "rejected", "file_id": file_id})

    def start(self):
        self.node.start_node()

    def stop(self):
        self.node.shutdown()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P2P Storage Node")
    parser.add_argument("--host", default="localhost", help="Host address of the storage node")
    parser.add_argument("--port", type=int, default=8002, help="Port of the storage node")
    parser.add_argument("--bootstrap", help="Bootstrap node address in the format 'host:port'")

    args = parser.parse_args()
    bootstrap = tuple(args.bootstrap.split(":")) if args.bootstrap else None

    storage_node = StorageNode(node_id=3, host=args.host, port=args.port, bootstrap_address=bootstrap)
    storage_node.start()

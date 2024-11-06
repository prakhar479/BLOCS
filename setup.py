from Crypto.PublicKey import RSA
import json
import hashlib
import os
import threading
from file_layer import Distribute, Assimilate
from network_layer import Network, Message
from typing import Optional, Dict, Any, Union
import socket

GENESIS_PORT = 5050  # Macro for Genesis Node port


class P2PFileStorageCLI:
    def __init__(self, ip: str = "localhost", port: int = 5050, genesis_ip: Optional[str] = None) -> None:
        self.network = Network(ip)
        self.port = port
        self.genesis_ip = genesis_ip
        # Stores file metadata: file_id -> {filename, size, extension, shard_mapping}
        self.file_table: Dict[str, Dict[str, Any]] = {}
        self.network.start(port)

        self.msg_gen = Message(sender_ip=ip, sender_port=port)

        # Join the network if not Genesis node
        if genesis_ip:
            self.network.join_network()

    def _generate_file_id(self, file_content: bytes) -> str:
        """Generate a unique file ID based on file content using SHA-256."""
        file_hash = hashlib.sha256(file_content).hexdigest()
        return file_hash

    def distribute_file(self, file_path: str, private_key: bytes) -> Optional[str]:
        """Distribute a file across the P2P network."""
        filename = os.path.basename(file_path)
        extension = os.path.splitext(filename)[1]
        file_size = os.path.getsize(file_path)

        # Determine number of shards based on available peers
        peers = self.network.get_connections()
        num_shards = len(peers)

        if num_shards < 1:
            print("Not enough peers to distribute the file.")
            return None

        with open(file_path, 'rb') as file_obj:
            file_content = file_obj.read()
            file_obj.seek(0)
            file_id = self._generate_file_id(file_content)
            encrypted_shards, shard_mapping = Distribute(
                file_obj, private_key, num_shards=num_shards)

        peer_mapping = {peer_indx: -1 for peer_indx in range(len(peers))}
        # Distribute shards to peers
        for shard_index, shard in enumerate(encrypted_shards):
            peer = peers[shard_index % len(peers)]
            self._send_shard(peer, shard, shard_index, file_id)
            peer_mapping[shard_index % len(peers)] = shard_index

        # Store file metadata in memory
        self.file_table[file_id] = {
            "filename": filename,
            "size": file_size,
            "extension": extension,
            "shard_mapping": shard_mapping,
            "peer_mapping": peer_mapping,
        }
        print(f"File '{filename}' distributed with File ID: {file_id}")
        return file_id

    def retrieve_file(self, file_id: str, private_key: bytes) -> Optional[str]:
        """Retrieve a file from the P2P network using its file ID."""
        file_info = self.file_table.get(file_id)
        if not file_info:
            print("File ID not found in table.")
            return None

        filename = file_info["filename"]
        shard_mapping = file_info["shard_mapping"]
        peer_mapping = file_info["peer_mapping"]

        peers = self.network.get_connections()

        # Retrieve each shard from its respective peer
        shards = []
        for peer_indx, shard_index in peer_mapping.items():
            shard = self._request_shard(peers[peer_indx], file_id, shard_index)
            if shard:
                shards.append(shard)
            else:
                print(f"Failed to retrieve shard {
                      shard_index} from peer {peers[peer_indx]}")

        # Reassemble file from shards
        original_data = Assimilate(
            shards, shard_mapping, private_key)
        output_path = f"retrieved_{filename}"
        with open(output_path, 'wb') as out_file:
            out_file.write(original_data)

        print(f"File '{filename}' retrieved and saved as '{output_path}'")
        return output_path

    def list_files(self) -> None:
        """List all files available in the network with metadata."""
        if not self.file_table:
            print("No files available.")
            return

        print("Files stored in the network:")
        for file_id, info in self.file_table.items():
            print(f"File ID: {file_id}")
            print(f"Filename: {info['filename']}")
            print(f"Size: {info['size']} bytes")
            print(f"Extension: {info['extension']}")
            print(f"Shards: {len(info['shard_mapping'])}")
            print("-" * 40)

    def _get_random_peer(self) -> Optional[str]:
        """Get a random peer from the network."""
        peers = self.network.get_all_peers()
        return peers[0] if peers else None

    def _send_shard(self, peer: str, shard: bytes, shard_index: int, file_id: str) -> None:
        """Send a shard to a peer."""
        message = {
            "file_id": file_id,
            "shard_index": shard_index,
            "shard_data": shard.hex()
        }
        response = self.network.send(peer, self.msg_gen.msg(
            message, "#STORE_SHARD"), hasResponse=1)
        print(f"Shard {shard_index} sent to peer {peer}")
        if response:
            if response == "success":
                print(f"Peer {peer} received shard {shard_index}")
            else:
                print(f"Peer {peer} failed to receive shard {shard_index}")

    def _request_shard(self, peer: socket.socket, file_id: str, shard_index: int) -> Optional[bytes]:
        """Request a specific shard from a peer."""
        message = {
            "file_id": file_id,
            "shard_index": shard_index
        }
        response = self.network.send(peer, self.msg_gen.msg(
            message, "#REQUEST_SHARD"), hasResponse=1)
        if response:
            shard_data = json.loads(response).get("message", {}).get("shard_data")
            return bytes.fromhex(shard_data) if shard_data else None
        return None

    def listen_for_messages(self) -> None:
        """Listen for incoming shard storage or retrieval requests."""
        self.network.handle_messages = self._handle_message

    def _handle_message(self, message: Dict[str, Any], conn: socket.socket) -> None:
        """Handle incoming messages based on type."""
        msg_type = message.get("title")
        message = message.get("message")

        if msg_type == "#STORE_SHARD":
            print("Received shard storage request.")
            file_id = message["file_id"]
            shard_index = message["shard_index"]
            shard_data = bytes.fromhex(message["shard_data"])
            os.makedirs(f"shards/{file_id}", exist_ok=True)
            with open(f"shards/{file_id}/shard_{shard_index}.bin", 'wb') as shard_file:
                shard_file.write(shard_data)
            print(f"Stored shard {shard_index} for file ID {file_id}")

            self.network.reply(
                conn, self.msg_gen.short_msg("#REPLY", "success"))

        elif msg_type == "#REQUEST_SHARD":
            print("Received shard retrieval request.")
            file_id = message["file_id"]
            shard_index = message["shard_index"]
            shard_path = f"shards/{file_id}/shard_{shard_index}.bin"
            if os.path.exists(shard_path):
                with open(shard_path, 'rb') as shard_file:
                    shard_data = shard_file.read()
                response_message = {
                    "shard_data": shard_data.hex()
                }

                self.network.reply(conn, self.msg_gen.msg(
                    response_message, "#REPLY"))
                print(f"Sent shard {shard_index} for file ID {file_id}")
            else:
                print(f"Shard {shard_index} for file ID {file_id} not found")


def main() -> None:
    is_genesis = input(
        "Is this a Genesis node? (yes/no): ").strip().lower() == "yes"
    port = GENESIS_PORT if is_genesis else int(
        input("Enter port number for this node: "))
    genesis_ip = None if is_genesis else input(
        "Enter Genesis IP: ").strip() or None

    cli = P2PFileStorageCLI(port=port, genesis_ip=genesis_ip)
    threading.Thread(target=cli.listen_for_messages, daemon=True).start()
    private_key = input(
        "Enter encryption key (for upload/download)(leave empty for auto-generation): ")
    if not private_key:
        private_key = RSA.generate(2048).export_key()
        print(f"Generated RSA key: {private_key.decode()}")
        print("Keep this key secure for file encryption/decryption.")
        print("-" * 40)

    while True:
        command = input(
            "Enter command (upload, download, list, clear, exit): ").strip().lower()

        try:
            if command == "upload":
                file_path = input("Enter path to file for upload: ")
                cli.distribute_file(file_path, private_key=private_key)

            elif command == "download":
                file_id = input("Enter File ID for download: ")
                cli.retrieve_file(file_id, private_key=private_key)

            elif command == "list":
                cli.list_files()

            elif command == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')

            elif command == "exit":
                cli.network.stop()
                print("Exiting program.")
                os._exit(0)

            else:
                print(
                    "Invalid command. Please use upload, download, list, clear, or exit.")
        except Exception as e:
            print(f"Error: {e}")
            y = input("Do you want a complete traceback? (yes/no): ")
            if y == "yes" or y == "y":
                raise e


if __name__ == "__main__":
    main()

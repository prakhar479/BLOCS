# network_layer/node.py

import socket
import threading
import pickle
from .handlers import DataPacket, DataHandler
from .utils import connect_socket
from .logger import logger
from .config import BUFFER_SIZE, MAX_CONNECTIONS, RETRY_COUNT

class Node:
    def __init__(self, node_id, host, port, bootstrap_address=None):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.bootstrap_address = bootstrap_address
        self.peers = set()  # Each peer is stored as a tuple (node_id, host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(MAX_CONNECTIONS)
        self.running = True

    def __str__(self):
        return f"Node {self.node_id} on {self.host}:{self.port}"

    def start_node(self):
        threading.Thread(target=self.listen_for_peers, daemon=True).start()
        if self.bootstrap_address:
            self.connect_to_bootstrap()
        logger.info(f"Node {self.node_id} started on {self.host}:{self.port}")

    def connect_to_bootstrap(self):
        try:
            s = connect_socket(*self.bootstrap_address)
            s.sendall(pickle.dumps((self.node_id, self.host, self.port)))
            peer_list = pickle.loads(s.recv(BUFFER_SIZE))
            self.peers.update(peer_list)
            logger.info(f"Node {self.node_id} connected to bootstrap; Peers: {self.peers}")
            s.close()
            self.connect_to_peers()
        except Exception as e:
            logger.error(f"Node {self.node_id} failed to connect to bootstrap: {e}")
            self.shutdown()

    def connect_to_peers(self):
        for peer in self.peers:
            peer_id, peer_host, peer_port = peer
            if peer_id != self.node_id:
                for attempt in range(RETRY_COUNT):
                    try:
                        s = connect_socket(peer_host, peer_port)
                        s.sendall(pickle.dumps(DataPacket(self.node_id, f"Hello from Node {self.node_id}")))
                        logger.info(f"Node {self.node_id} connected to peer {peer_id} at {peer_host}:{peer_port}")
                        s.close()
                        break
                    except Exception as e:
                        logger.warning(f"Node {self.node_id} failed to connect to peer {peer_id} "
                                       f"at {peer_host}:{peer_port} on attempt {attempt + 1}: {e}")
                        if attempt == RETRY_COUNT - 1:
                            logger.error(f"Node {self.node_id} exhausted retries for peer {peer_id}")

    def listen_for_peers(self):
        while self.running:
            try:
                conn, _ = self.socket.accept()
                threading.Thread(target=self.handle_peer, args=(conn,), daemon=True).start()
            except Exception as e:
                logger.error(f"Node {self.node_id} encountered error while listening for peers: {e}")
                self.shutdown()

    def handle_peer(self, conn):
        try:
            data = conn.recv(BUFFER_SIZE)
            packet = pickle.loads(data)
            self.handle_data(packet)
        except Exception as e:
            logger.error(f"Node {self.node_id} failed to handle data from peer: {e}")
        finally:
            conn.close()

    def send_data(self, peer, data):
        try:
            peer_id, peer_host, peer_port = peer
            s = connect_socket(peer_host, peer_port)
            packet = DataPacket(self.node_id, data)
            s.sendall(pickle.dumps(packet))
            s.close()
            logger.info(f"Node {self.node_id} sent data to peer {peer_id} at {peer_host}:{peer_port}")
        except Exception as e:
            logger.error(f"Node {self.node_id} failed to send data to peer {peer_id} at {peer_host}:{peer_port}: {e}")

    def broadcast_data(self, data):
        for peer in self.peers:
            self.send_data(peer, data)

    def handle_data(self, packet):
        DataHandler.handle_data(self, packet)

    def shutdown(self):
        self.running = False
        self.socket.close()
        logger.info(f"Node {self.node_id} on {self.host}:{self.port} has shut down.")

# network_layer/bootstrap_node.py

import pickle
import threading
from .node import Node
from .logger import logger
from .config import BUFFER_SIZE

class BootstrapNode(Node):
    def __init__(self, node_id, host, port):
        super().__init__(node_id, host, port)
        self.peers = set()

    def start_bootstrap_node(self):
        threading.Thread(target=self.listen_for_peers, daemon=True).start()
        logger.info(f"Bootstrap node {self.node_id} started on {self.host}:{self.port}")

    def handle_peer(self, conn):
        try:
            data = conn.recv(BUFFER_SIZE)
            new_peer = pickle.loads(data)
            conn.sendall(pickle.dumps(list(self.peers)))
            self.peers.add(new_peer)
            logger.info(f"Bootstrap node {self.node_id} added new peer: {new_peer}")
            logger.info(f"Updated peers list: {self.peers}")
        except Exception as e:
            logger.error(f"Bootstrap node {self.node_id} failed to handle new peer: {e}")
        finally:
            conn.close()

    def shutdown(self):
        super().shutdown()
        logger.info(f"Bootstrap node {self.node_id} has shut down.")

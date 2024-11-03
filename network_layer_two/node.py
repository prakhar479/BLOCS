# network_layer/node.py

from pyp2p.net import Net
from .config import DEFAULT_INTERFACE, DEBUG
import threading
import time

class Node:
    def __init__(self, node_id, ip, port, interface, bootstrap_ip, bootstrap_port, debug=0):
        self.node = Net(
            passive_bind=ip,
            passive_port=port,
            interface=interface,
            node_type="passive",
            debug=debug
        )
        self.node_id = node_id
        self.bootstrap_ip = bootstrap_ip
        self.bootstrap_port = bootstrap_port
        self.node.disable_bootstrap()
        self.node.disable_advertise()
        self.node.start()
        self.peers = set()

    def start_node(self):
        self.register_with_bootstrap()
        self.discover_peers()
        threading.Thread(target=self.listen).start()

    def register_with_bootstrap(self):
        """Register this node with the bootstrap node."""
        bootstrap_con = Net(
            passive_bind=self.bootstrap_ip,
            passive_port=self.bootstrap_port,
            interface=DEFAULT_INTERFACE,
            node_type="active",
            debug=DEBUG
        )
        bootstrap_con.start()
        bootstrap_con.send_line(f"register:{self.node_id}:{self.node.bind_ip}:{self.node.bind_port}")
        bootstrap_con.stop()

    def discover_peers(self):
        """Request peer list from bootstrap and connect to peers."""
        bootstrap_con = Net(
            passive_bind=self.bootstrap_ip,
            passive_port=self.bootstrap_port,
            interface=DEFAULT_INTERFACE,
            node_type="active",
            debug=DEBUG
        )
        bootstrap_con.start()
        bootstrap_con.send_line("get_peers")
        
        for con in bootstrap_con:
            for reply in con:
                if reply.startswith("peers:"):
                    peer_addresses = reply.split(":")[1].split(",")
                    for address in peer_addresses:
                        ip, port = address.split(":")
                        self.connect_to_peer(ip, int(port))
        bootstrap_con.stop()

    def connect_to_peer(self, ip, port):
        """Establish connection with a new peer."""
        peer_con = Net(
            passive_bind=ip,
            passive_port=port,
            interface=DEFAULT_INTERFACE,
            node_type="active",
            debug=DEBUG
        )
        peer_con.start()
        self.peers.add(peer_con)
        print(f"Connected to peer at {ip}:{port}")

    def handle_data(self, data):
        """Default handler for incoming data. Override this method as needed."""
        print(f"Data received: {data}")

    def send_data(self, data, peer):
        peer.send_line(data)

    def broadcast_data(self, data):
        for peer in self.peers:
            peer.send_line(data)

    def listen(self):
        """Continuously listen for incoming data."""
        while True:
            for con in self.node:
                for reply in con:
                    self.handle_data(reply)
            time.sleep(1)

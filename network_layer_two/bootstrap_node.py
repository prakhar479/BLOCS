# network_layer/bootstrap_node.py

from pyp2p.net import Net
# import threading
import time

class BootstrapNode:
    def __init__(self, ip, port, interface, debug=0):
        self.node = Net(
            passive_bind=ip,
            passive_port=port,
            interface=interface,
            node_type="passive",
            debug=debug
        )
        self.node.disable_bootstrap()
        self.node.disable_advertise()
        self.node.start()
        self.peers = {}  # Dictionary to store peer details

    def start_bootstrap_node(self):
        print("Bootstrap node started.")
        self.event_loop()

    def register_peer(self, peer_id, address):
        """Register a peer in the peers dictionary."""
        self.peers[peer_id] = address

    def get_peers(self):
        """Return a list of peers excluding the bootstrap node itself."""
        return list(self.peers.values())

    def event_loop(self):
        """Main loop to handle incoming peer connections and registrations."""
        while True:
            for con in self.node:
                for reply in con:
                    # Expecting registration requests in the form of "register:<peer_id>:<address>"
                    if reply.startswith("register:"):
                        _, peer_id, address = reply.split(":")
                        self.register_peer(peer_id, address)
                        print(f"Registered peer {peer_id} at {address}")
                    elif reply == "get_peers":
                        # Send peer list to the requesting node
                        con.send_line("peers:" + ",".join(self.get_peers()))

            # Remove disconnected peers
            for peer_id, address in list(self.peers.items()):
                if not any(peer_id == con.id for con in self.node):
                    print(f"Removing disconnected peer {peer_id}")
                    del self.peers[peer_id]

            time.sleep(1)

# network_layer/tests/test_network.py
from network_layer_two.bootstrap_node import BootstrapNode
from network_layer_two.node import Node
import threading

CONFIG = {
    "bootstrap_ip": "192.168.0.45",
    "bootstrap_port": 44444,
    "node_port": 44445,
    "interface": "eth0",
    "debug": 1
}


def test_bootstrap_node():
    bootstrap_node = BootstrapNode(
        CONFIG["bootstrap_ip"], CONFIG["bootstrap_port"], CONFIG["interface"], CONFIG["debug"]
    )
    threading.Thread(target=bootstrap_node.start_bootstrap_node).start()
    assert bootstrap_node.node is not None

def test_peer_registration_and_discovery():
    bootstrap_node = BootstrapNode(
        CONFIG["bootstrap_ip"], CONFIG["bootstrap_port"], CONFIG["interface"], CONFIG["debug"]
    )
    threading.Thread(target=bootstrap_node.start_bootstrap_node).start()

    node_1 = Node(
        node_id="node1",
        ip="192.168.0.46",
        port=44446,
        interface="eth0:1",
        bootstrap_ip=CONFIG["bootstrap_ip"],
        bootstrap_port=CONFIG["bootstrap_port"],
        debug=CONFIG["debug"]
    )
    node_1.start_node()

    node_2 = Node(
        node_id="node2",
        ip="192.168.0.47",
        port=44447,
        interface="eth0:2",
        bootstrap_ip=CONFIG["bootstrap_ip"],
        bootstrap_port=CONFIG["bootstrap_port"],
        debug=CONFIG["debug"]
    )
    node_2.start_node()

    # Ensure node1 and node2 are registered with the bootstrap node
    assert "node1" in bootstrap_node.peers
    assert "node2" in bootstrap_node.peers

    # Verify node1 and node2 can connect to each other after discovery
    assert any(peer.bind_ip == "192.168.0.47" for peer in node_1.peers)
    assert any(peer.bind_ip == "192.168.0.46" for peer in node_2.peers)

# network_layer/tests/test_network.py
from network_layer.bootstrap_node import BootstrapNode
from network_layer.node import Node

import time

BOOT_PORT = 12345
STORAGE_PORT = 9901
CLIENT_PORT = 9602

def test_bootstrapping():
    bootstrap_node = BootstrapNode(node_id=1, host="localhost", port=BOOT_PORT)
    bootstrap_node.start_bootstrap_node()

    storage_node = Node(node_id=2, host="localhost", port=STORAGE_PORT, bootstrap_address=("localhost", BOOT_PORT))
    storage_node.start_node()

    client_node = Node(node_id=3, host="localhost", port=CLIENT_PORT, bootstrap_address=("localhost", BOOT_PORT))
    client_node.start_node()

    time.sleep(1)   

    assert(len(bootstrap_node.peers) == 2)
    assert(len(storage_node.peers) == 0)
    assert(len(client_node.peers) == 1)
    

    storage_node.shutdown()
    client_node.shutdown()
    bootstrap_node.shutdown()

def test_communication():
    bootstrap_node = BootstrapNode(node_id=1, host="localhost", port=BOOT_PORT)
    bootstrap_node.start_bootstrap_node()

    storage_node = Node(node_id=2, host="localhost", port=STORAGE_PORT, bootstrap_address=("localhost", BOOT_PORT))
    storage_node.start_node()

    client_node = Node(node_id=3, host="localhost", port=CLIENT_PORT, bootstrap_address=("localhost", BOOT_PORT))
    client_node.start_node()

    time.sleep(1)

    assert(len(bootstrap_node.peers) == 2)
    assert(len(storage_node.peers) == 0)
    assert(len(client_node.peers) == 1)

    time.sleep(1)

    recieved_messages = []

    storage_node.handle_data = lambda packet: recieved_messages.append(packet)
    client_node.send_data("Hello from client!")

    time.sleep(1)

    assert(len(recieved_messages) == 1)
    assert(recieved_messages[0].data == "Hello from client!")


    storage_node.shutdown()
    client_node.shutdown()
    bootstrap_node.shutdown()

test_bootstrapping()

# network_layer/handlers.py

class DataPacket:
    def __init__(self, sender_id, data):
        self.sender_id = sender_id
        self.data = data

    def __str__(self):
        return f"{self.sender_id}: {self.data}"

class DataHandler:
    @staticmethod
    def handle_data(node, packet):
        print(f"Node {node.node_id} received data: {packet}")

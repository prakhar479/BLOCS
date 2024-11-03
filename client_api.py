from flask import Flask, jsonify, request
from client import Client

app = Flask(__name__)
client = None

@app.route("/upload", methods=["POST"])
def upload_file():
    file_path = request.json.get("file_path")
    private_key = request.json.get("private_key")
    if file_path and private_key:
        client.upload_file(file_path, private_key.encode())
        return jsonify({"status": "File uploaded successfully"}), 200
    return jsonify({"error": "Invalid parameters"}), 400

@app.route("/retrieve", methods=["POST"])
def retrieve_file():
    file_id = request.json.get("file_id")
    output_path = request.json.get("output_path")
    private_key = request.json.get("private_key")
    if file_id and output_path and private_key:
        client.retrieve_file(file_id, output_path, private_key.encode())
        return jsonify({"status": "File retrieved successfully"}), 200
    return jsonify({"error": "Invalid parameters"}), 400

@app.route("/list", methods=["GET"])
def list_files():
    files = client.list_files()
    return jsonify(files), 200

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="P2P Client REST API Server")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    client = Client(node_id=2, host="localhost", port=8001, bootstrap_address=None)
    client.start()
    app.run(host=args.host, port=args.port)
    client.stop()

import time

from web3 import Web3
import json

rpc_server = "HTTP://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(rpc_server))

contract_address = "0xB2fdf1B14056e4b22549D64844c2A93f9c33f3D7"


with open("abi.json", "r") as abi_file:
    contract_abi = json.load(abi_file)

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

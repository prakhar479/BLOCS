import time

from web3 import Web3
import json

rpc_server = "HTTP://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(rpc_server))

contract_address = "0xA09B19128f920Bca0D217308c831f0f0061B6cfa"


with open("abi.json", "r") as abi_file:
    contract_abi = json.load(abi_file)

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

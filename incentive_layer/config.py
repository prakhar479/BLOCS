import json
from web3 import Web3
import os


# Configuration for available networks
NETWORKS = {
    "mainnet": "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID",
    "goerli": "https://goerli.infura.io/v3/YOUR_INFURA_PROJECT_ID",
    "sepolia": "https://sepolia-rollup.arbitrum.io/rpc",
    "local": "http://127.0.0.1:7545"  # Local Ganache
}


class BlockchainConfig:
    def __init__(self, network="sepolia"):
        # Check if network is valid
        if network not in NETWORKS:
            raise ValueError(f"Unsupported network '{network}'. Available networks: {list(NETWORKS.keys())}")
        
        # Initialize the Web3 object with the appropriate RPC URL
        rpc_url = NETWORKS[network]
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Could not connect to the {network} network at {rpc_url}")

        # Load ABI from a specified file path
        abi_path = os.path.join(os.path.dirname(__file__), "abi.json")
        with open(abi_path, "r") as abi_file:
            self.contract_abi = json.load(abi_file)
        
        # Contract address for each network (use separate addresses for production if needed)
        self.contract_address = {
            "mainnet": "YOUR_MAINNET_CONTRACT_ADDRESS",
            "goerli": "YOUR_GOERLI_CONTRACT_ADDRESS",
            "sepolia": "YOUR_SEPOLIA_CONTRACT_ADDRESS",
            "local": "0xA09B19128f920Bca0D217308c831f0f0061B6cfa"
        }.get(network)
        
        if not self.contract_address:
            raise ValueError(f"No contract address specified for network '{network}'")

        # Initialize the contract object
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)

    def get_w3(self):
        return self.w3

    def get_contract(self):
        return self.contract


# Usage
# Initialize with 'sepolia' or 'mainnet' or 'goerli' or 'local'
try:
    config = BlockchainConfig(network="sepolia")
    w3 = config.get_w3()
    contract = config.get_contract()
except Exception as e:
    print(f"Initialization failed: {e}")

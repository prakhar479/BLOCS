import string
import time

from web3 import Web3
import json

# Initialize Web3 connection to your local Ganache RPC server
rpc_server = "HTTP://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(rpc_server))

# Set up contract and account details
contract_address = "0x63816C0Ee0B84567F37FD87FfDc90ECFf754583a"
my_address = "0x7673bC66b27131Edfc82eCa57e6197fF101eb965"
private_key = "0xc49e420df39797b7c441c2d2a95cd706e4549d06a18fe96c695d259500025407"

# Load ABI from abi.json file
with open("abi.json", "r") as abi_file:
    contract_abi = json.load(abi_file)

# Instantiate the contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Example function: Propose a deal
def propose_deal(file_id, storage_space, duration_hours):
    block_number = w3.eth.block_number
    print(f"Current block number: {block_number}")

    # If you need both block number and timestamp:
    block = w3.eth.get_block('latest')
    print(f"Block number: {block.number}")
    print(f"Block timestamp: {block.timestamp}")
    # Build transaction
    transaction = contract.functions.proposeDeal(file_id, storage_space, duration_hours).build_transaction({
        'from': my_address,
        'gas': 2000000,
        'gasPrice': w3.to_wei('50', 'gwei'),
        'nonce': w3.eth.get_transaction_count(my_address)
    })
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    return w3.to_hex(tx_hash)
def approve_deal(file_id, billing_amount):
    block_number = w3.eth.block_number
    print(f"Current block number: {block_number}")

    # If you need both block number and timestamp:
    block = w3.eth.get_block('latest')
    print(f"Block number: {block.number}")
    print(f"Block timestamp: {block.timestamp}")
    transaction = contract.functions.approveDeal(file_id, billing_amount).build_transaction({
        'from': my_address,
        'gas': 2000000,
        'gasPrice': w3.to_wei('50', 'gwei'),
        'nonce': w3.eth.get_transaction_count(my_address)
    })
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    return w3.to_hex(tx_hash)


def validate_proof(file_id):
    block_number = w3.eth.block_number
    print(f"Current block number: {block_number}")

    # If you need both block number and timestamp:
    block = w3.eth.get_block('latest')
    print(f"Block number: {block.number}")
    print(f"Block timestamp: {block.timestamp}")
    try:
        # Estimate gas first to check if the transaction will fail
        gas_estimate = contract.functions.validateProof(file_id).estimate_gas({
            'from': my_address
        })

        # Build transaction with estimated gas
        transaction = contract.functions.validateProof(file_id).build_transaction({
            'from': my_address,
            'gas': 6721975,  # Use estimated gas instead of hardcoded value
            'gasPrice': w3.eth.gas_price,  # Get current gas price
            'nonce': w3.eth.get_transaction_count(my_address)
        })

        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt['status'] == 1:
            return w3.to_hex(tx_hash)
        else:
            raise Exception("Transaction failed")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise
def invalidate_deal(file_id, reason):
    block_number = w3.eth.block_number
    print(f"Current block number: {block_number}")

    # If you need both block number and timestamp:
    block = w3.eth.get_block('latest')
    print(f"Block number: {block.number}")
    print(f"Block timestamp: {block.timestamp}")
    print(contract.blocknumber)
    transaction = contract.functions.invalidateDeal(file_id, reason).build_transaction({
        'from': my_address,
        'gas': 2000000,
        'gasPrice': w3.to_wei('50', 'gwei'),
        'nonce': w3.eth.get_transaction_count(my_address)
    })
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    return w3.to_hex(tx_hash)
def get_deal_status(file_id):
    deal = contract.functions.files(file_id).call()
    return {
        "client": deal[0],
        "storageProvider": deal[1],
        "startTime": deal[2],
        "duration": deal[3],
        "storageSpace": deal[4],
        "totalAmount": deal[5],
        "remainingAmount": deal[6],
        "lastValidationTime": deal[7],
        "isActive": deal[8],
        "isApproved": deal[9]
    }
import random
text = 'tTsKzVtdWa'

file_id = w3.keccak(text='PZHtkZseoQ')
storage_space = 10
duration_hours = 1
print(text)
# Propose a deal
# tx_hash_propose = propose_deal(file_id, storage_space, duration_hours)
# print(f"Propose Deal Transaction hash: {tx_hash_propose}")
# 1730810861
# 1730810861
# # Approve a deal 243 244

# billing_amount = contract.functions.calculateTotalAmount(storage_space, duration_hours).call()
# tx_hash_approve = approve_deal(file_id, billing_amount)
# print(f"Approve Deal Transaction hash: {tx_hash_approve}")
# time.sleep(1)
# Validate proof
tx_hash_validate = validate_proof(file_id)
print(f"Validate Proof Transaction hash: {tx_hash_validate}")

# Invalidate a deal (if needed)
reason = "Client no longer requires storage"
tx_hash_invalidate = invalidate_deal(file_id, reason)
print(f"Invalidate Deal Transaction hash: {tx_hash_invalidate}")

# Check deal status
status = get_deal_status(file_id)
print("Deal Status:", status)
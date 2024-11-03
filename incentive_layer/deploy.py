from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

class ContractorFileStorageAPI:
    def __init__(self, provider_url, contract_address, abi):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        assert self.web3.is_connected(), "Failed to connect to the blockchain."

        self.contract = self.web3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )

    def deposit(self, private_key):
        account = self.web3.eth.account.from_key(private_key)
        tx = self.contract.functions.deposit().build_transaction({
            'from': account.address,
            'value': self.web3.to_wei(1, 'ether'),  # Change the amount as needed
            'nonce': self.web3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': self.web3.eth.gas_price
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)

        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        return self.web3.to_hex(tx_hash)

    def set_user_public_key(self, private_key, public_key):
        account = self.web3.eth.account.from_key(private_key)
        tx = self.contract.functions.setUserPublicKey(public_key).build_transaction({
            'from': account.address,
            'nonce': self.web3.eth.get_transaction_count(account.address),
            'gas': 100000,
            'gasPrice': self.web3.eth.gas_price
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return self.web3.to_hex(tx_hash)

    def withdraw(self, private_key, amount):
        account = self.web3.eth.account.from_key(private_key)
        tx = self.contract.functions.withdraw(amount).build_transaction({
            'from': account.address,
            'nonce': self.web3.eth.get_transaction_count(account.address),
            'gas': 100000,
            'gasPrice': self.web3.eth.gas_price
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return self.web3.to_hex(tx_hash)

    def initialize_file_storage(self, private_key, client, file_id, file_hash, total_shards, total_size, duration, payment):
        account = self.web3.eth.account.from_key(private_key)
        tx = self.contract.functions.initializeFileStorage(
            Web3.to_checksum_address(client),
            file_id,
            file_hash,
            total_shards,
            total_size,
            duration,
            payment
        ).build_transaction({
            'from': account.address,
            'nonce': self.web3.eth.get_transaction_count(account.address),
            'gas': 300000,
            'gasPrice': self.web3.eth.gas_price
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return self.web3.to_hex(tx_hash)

    def store_shard(self, private_key, client, file_id, shard_index, shard_hash, shard_size):
        account = self.web3.eth.account.from_key(private_key)
        tx = self.contract.functions.storeShard(
            Web3.to_checksum_address(client),
            file_id,
            shard_index,
            shard_hash,
            shard_size
        ).build_transaction({
            'from': account.address,
            'nonce': self.web3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': self.web3.eth.gas_price
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return self.web3.to_hex(tx_hash)

    def submit_shard_proof(self, private_key, client, file_id, shard_index, proof_hash):
        account = self.web3.eth.account.from_key(private_key)
        tx = self.contract.functions.submitShardProof(
            Web3.to_checksum_address(client),
            file_id,
            shard_index,
            proof_hash
        ).build_transaction({
            'from': account.address,
            'nonce': self.web3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': self.web3.eth.gas_price
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return self.web3.to_hex(tx_hash)

    def complete_deal(self, private_key, server, client, file_id):
        account = self.web3.eth.account.from_key(private_key)
        tx = self.contract.functions.completeDeal(
            Web3.to_checksum_address(server),
            Web3.to_checksum_address(client),
            file_id
        ).build_transaction({
            'from': account.address,
            'nonce': self.web3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': self.web3.eth.gas_price
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return self.web3.to_hex(tx_hash)

    def get_file_metadata(self, server, client, file_id):
        return self.contract.functions.getFileMetadata(
            Web3.to_checksum_address(server),
            Web3.to_checksum_address(client),
            file_id
        ).call()

    def get_shard_info(self, server, client, file_id, shard_index):
        return self.contract.functions.getShardInfo(
            Web3.to_checksum_address(server),
            Web3.to_checksum_address(client),
            file_id,
            shard_index
        ).call()

    def get_deal_terms(self, server, client, file_id):
        return self.contract.functions.getDealTerms(
            Web3.to_checksum_address(server),
            Web3.to_checksum_address(client),
            file_id
        ).call()

import json
from web3 import Web3
from deploy import ContractorFileStorageAPI


def load_abi(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

web3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))


def contract_storage():
    # Configuration
    PROVIDER_URL = "http://127.0.0.1:7545"
    CONTRACT_ADDRESS = "0x48B43A180bAA78f4b22d2C936e3D545403948087"
    PRIVATE_KEY = "0xf9ced50009328e9d1e21220c4705607781d2287ca7794b9227eb917db47d6e34"

    # Load ABI
    abi = load_abi('abi.json')

    # Initialize API
    try:
        api = ContractorFileStorageAPI(PROVIDER_URL, CONTRACT_ADDRESS, abi)
        print("✅ API initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize API: {str(e)}")
        return

    # Get account address from private key
    account = web3.eth.account.from_key(PRIVATE_KEY)
    CLIENT_ADDRESS = account.address

    # Test cases
    try:
        # 1. Test deposit
        print("\n📝 Testing deposit...")
        tx_hash = api.deposit(PRIVATE_KEY)
        print(f"✅ Deposit successful. Transaction hash: {tx_hash}")

        # 2. Test setting public key
        print("\n📝 Testing set_user_public_key...")
        public_key = "0x123456789abcdef"  # Example public key
        tx_hash = api.set_user_public_key(PRIVATE_KEY, public_key)
        print(f"✅ Public key set. Transaction hash: {tx_hash}")

        # 3. Test file storage initialization
        print("\n📝 Testing initialize_file_storage...")
        file_id = "test_file_1"
        file_hash = Web3.keccak(text="test_file_content NIGA BIGA CHIGA").hex()
        total_shards = 3
        total_size = 1  # bytes
        duration = 30  # days
        payment = Web3.to_wei(0.1, 'ether')  # 0.1 ETH

        tx_hash = api.initialize_file_storage(
            PRIVATE_KEY,
            CLIENT_ADDRESS,
            file_id,
            file_hash,
            total_shards,
            total_size,
            duration,
            payment
        )
        print(f"✅ File storage initialized. Transaction hash: {tx_hash}")

        # 4. Test storing shards
        print("\n📝 Testing store_shard...")
        for shard_index in range(total_shards):
            shard_hash = Web3.keccak(text=f"shard_{shard_index}").hex()
            shard_size = total_size // total_shards

            tx_hash = api.store_shard(
                PRIVATE_KEY,
                CLIENT_ADDRESS,
                file_id,
                shard_index,
                shard_hash,
                shard_size
            )
            print(f"✅ Shard {shard_index} stored. Transaction hash: {tx_hash}")

        # 5. Test submitting proofs
        print("\n📝 Testing submit_shard_proof...")
        for shard_index in range(total_shards):
            proof_hash = Web3.keccak(text=f"proof_{shard_index}").hex()

            tx_hash = api.submit_shard_proof(
                PRIVATE_KEY,
                CLIENT_ADDRESS,
                file_id,
                shard_index,
                proof_hash
            )
            print(f"✅ Proof submitted for shard {shard_index}. Transaction hash: {tx_hash}")

        # 6. Test getting file metadata
        print("\n📝 Testing get_file_metadata...")
        metadata = api.get_file_metadata(account.address, CLIENT_ADDRESS, file_id)
        print(f"✅ File metadata retrieved: {metadata}")

        # 7. Test getting shard info
        print("\n📝 Testing get_shard_info...")
        shard_info = api.get_shard_info(account.address, CLIENT_ADDRESS, file_id, 0)
        print(f"✅ Shard info retrieved: {shard_info}")

        # 8. Test getting deal terms
        print("\n📝 Testing get_deal_terms...")
        deal_terms = api.get_deal_terms(account.address, CLIENT_ADDRESS, file_id)
        print(f"✅ Deal terms retrieved: {deal_terms}")

        # 9. Test completing the deal
        print("\n📝 Testing complete_deal...")
        tx_hash = api.complete_deal(PRIVATE_KEY, account.address, CLIENT_ADDRESS, file_id)
        print(f"✅ Deal completed. Transaction hash: {tx_hash}")

        # 10. Test withdrawal
        print("\n📝 Testing withdraw...")
        withdraw_amount = Web3.to_wei(0.05, 'ether')  # Withdraw 0.05 ETH
        tx_hash = api.withdraw(PRIVATE_KEY, withdraw_amount)
        print(f"✅ Withdrawal successful. Transaction hash: {tx_hash}")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    contract_storage()
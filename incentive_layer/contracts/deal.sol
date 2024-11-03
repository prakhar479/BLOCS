pragma solidity >=0.4.22 <0.9.0;

contract ContractorFileStorage {
    constructor(){}
    struct FileShard {
        bytes32 hashedShardWithKey;      // SHA256 hash of the shard hash
        uint256 size;           // Size of shard in bytes
        uint256 timestamp;      // When the shard was stored
        bool isActive;          // Whether shard is currently stored
        uint256 lastProofTime;  // Last time proof was submitted
    }
    
    struct FileMetadata {
        bytes32 fileHash;       // Complete file hash
        uint256 totalShards;    // Total number of shards for this file
        uint256 totalSize;      // Total file size
        mapping(uint256 => FileShard) shards; // Mapping of shard index to shard data
    }
    
    struct DealTerms {
        uint256 duration;       // Duration of storage deal
        uint256 payment;        // Payment amount for storage
        uint256 startTime;      // When the deal started
        bool isActive;          // Whether deal is active
    }
    
    // Server => Client => FileID => FileMetadata
    mapping(address => mapping(address => mapping(bytes32 => FileMetadata))) public files;
    
    // Server => Client => FileID => DealTerms
    mapping(address => mapping(address => mapping(bytes32 => DealTerms))) public deals;
    // mapping(address => mapping(bytes32 => FileShard)) public shards;  // User => ShardID => Shard details

    // Balance tracking
    mapping(address => uint256) public balance;
    mapping(address => bytes32) public userPublicKeys;

    
    uint256 constant MAX_DURATION = 30 days;
    uint256 constant PROOF_INTERVAL = 10 hours;
    
    event FileStored(
        address indexed server,
        address indexed client,
        bytes32 indexed fileId,
        bytes32 fileHash,
        uint256 totalShards
    );
    
    event ShardStored(
        address indexed server,
        address indexed client,
        bytes32 indexed fileId,
        uint256 shardIndex,
        bytes32 shardHash
    );
    
    event ProofSubmitted(
        address indexed server,
        address indexed client,
        bytes32 indexed fileId,
        uint256 shardIndex,
        uint256 timestamp
    );
    
    event DealCreated(
        address indexed server,
        address indexed client,
        bytes32 indexed fileId,
        uint256 payment,
        uint256 duration
    );

    receive() external payable {}
    
    function deposit() external payable {
        balance[msg.sender] += msg.value;
    }
    
    function setUserPublicKey(bytes32 publicKey) external {
        userPublicKeys[msg.sender] = publicKey;
    }
    function withdraw(uint256 amount) external {
        require(balance[msg.sender] >= amount, "Insufficient balance");
        balance[msg.sender] -= amount;
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Transfer failed");
    }
    
    function initializeFileStorage(
        address client,
        bytes32 fileId,
        bytes32 fileHash,
        uint256 totalShards,
        uint256 totalSize,
        uint256 duration,
        uint256 payment
    ) external {
        require(duration <= MAX_DURATION, "Duration exceeds maximum");
        require(payment > 0, "Payment required");
        require(totalShards > 0, "Must have at least one shard");
        require(balance[client] >= payment, "Insufficient client balance");
        FileMetadata storage fileMetadata = files[msg.sender][client][fileId];
        fileMetadata.fileHash = fileHash;
        fileMetadata.totalShards = totalShards;
        fileMetadata.totalSize = totalSize;
        
        DealTerms storage dealTerms = deals[msg.sender][client][fileId];
        dealTerms.duration = duration;
        dealTerms.payment = payment;
        dealTerms.startTime = block.timestamp;
        dealTerms.isActive = true;
        
        
        balance[client] -= payment;
        
        emit FileStored(msg.sender, client, fileId, fileHash, totalShards);
        emit DealCreated(msg.sender, client, fileId, payment, duration);
    }
    
        function storeShard(
        address client,
        bytes32 fileId,
        uint256 shardIndex,
        bytes32 shardHash,
        uint256 shardSize

    ) external {
        require(deals[msg.sender][client][fileId].isActive, "No active deal");

        FileShard storage shard = files[msg.sender][client][fileId].shards[shardIndex];
        require(!shard.isActive, "Shard already stored");
        bytes32 userPublicKey = userPublicKeys[client];
        // Hash the shardHash with the user's public key to create a unique identifier
        bytes32 hashWithKey = keccak256(abi.encodePacked(shardHash, userPublicKey));
        
        // Store the hashed shard with user public key
        shard.hashedShardWithKey = hashWithKey;
        shard.size = shardSize;
        shard.timestamp = block.timestamp;
        shard.isActive = true;
        shard.lastProofTime = block.timestamp;

        emit ShardStored(msg.sender, client, fileId, shardIndex, shardHash);
    }

    function submitShardProof(
    address client,
    bytes32 fileId,
    uint256 shardIndex,
    bytes32 proofHash
    ) external {
        DealTerms storage deal = deals[msg.sender][client][fileId];
        require(deal.isActive, "No active deal");
        require(block.timestamp <= deal.startTime + deal.duration, "Deal expired");
        bytes32 userPublicKey = userPublicKeys[client];
        FileShard storage shard = files[msg.sender][client][fileId].shards[shardIndex];
        require(shard.isActive, "Shard not active");
        require(
            block.timestamp >= shard.lastProofTime + PROOF_INTERVAL,
            "Too early for proof"
        );
        
        bytes32 computedHash = keccak256(abi.encodePacked(proofHash, userPublicKey));
        
        require(computedHash == shard.hashedShardWithKey, "Invalid proof");
        
        shard.lastProofTime = block.timestamp;
        
        emit ProofSubmitted(msg.sender, client, fileId, shardIndex, block.timestamp);
    }

    
    function completeDeal(
        address server,
        address client,
        bytes32 fileId
    ) external {
        DealTerms storage deal = deals[server][client][fileId];
        require(deal.isActive, "No active deal");
        require(
            block.timestamp >= deal.startTime + deal.duration,
            "Deal not expired"
        );
        
        FileMetadata storage file = files[server][client][fileId];
        bool allProofsValid = true;
        

        for(uint256 i = 0; i < file.totalShards; i++) {
            FileShard storage shard = file.shards[i];
            if(shard.isActive) {
                if(shard.lastProofTime + PROOF_INTERVAL < block.timestamp) {
                    allProofsValid = false;
                    break;
                }
            }
        }
        
        if(allProofsValid) {
            balance[server] += deal.payment;
        } else {
            balance[client] += deal.payment;
        }
        
        deal.isActive = false;
    }
    

    function getFileMetadata(
        address server,
        address client,
        bytes32 fileId
    ) external view returns (
        bytes32 fileHash,
        uint256 totalShards,
        uint256 totalSize,
        bool isActive
    ) {
        FileMetadata storage file = files[server][client][fileId];
        DealTerms storage deal = deals[server][client][fileId];
        return (
            file.fileHash,
            file.totalShards,
            file.totalSize,
            deal.isActive
        );
    }
    
    function getShardInfo(
        address server,
        address client,
        bytes32 fileId,
        uint256 shardIndex
    ) external view returns (
        bytes32 hashedShardWithKey,
        uint256 size,
        uint256 timestamp,
        bool isActive,
        uint256 lastProofTime
    ) {
        FileShard storage shard = files[server][client][fileId].shards[shardIndex];
        return (
            shard.hashedShardWithKey,
            shard.size,
            shard.timestamp,
            shard.isActive,
            shard.lastProofTime
        );
    }
    
    function getDealTerms(
        address server,
        address client,
        bytes32 fileId
    ) external view returns (
        uint256 duration,
        uint256 payment,
        uint256 startTime,
        bool isActive
    ) {
        DealTerms storage deal = deals[server][client][fileId];
        return (
            deal.duration,
            deal.payment,
            deal.startTime,
            deal.isActive
        );
    }
}

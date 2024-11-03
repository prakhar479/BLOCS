pragma solidity ^0.8.13;

contract Contractor {
    /*
    The client and server make a deal.
    1. Client deposits certain amount of ether to the contract and mentions duration.
    2. Duration can be set to max 30 days after which client has to renew the file.
    3. Server will have to send the proofs every 10 hours
    4. At the end of time, deposit is gone to server.
    5. If server fails to send proof, deposit is sent back to client's file
   */
   /**
      1. People cam fund ether in their account.
      2. They can also withdraw ether too.
   */
    mapping(address => mapping(address => uint256)) public deal; // lender(server)=>borrower(client)=>value
    mapping(address => uint256) public balance; // balance in people's account
    mapping(address => mapping(address => uint256)) public timeOfDeal; // lender(server)=>borrower(client)=>time of deal
    mapping(address => mapping(address => uint256)) public lastProofTime; // lender(server)=>borrower(client)=>time of proof
    mapping(address => mapping(address => uint256)) public dealDuration; // lender(server)=>borrower(client)=>holding time
    
    uint256 constant MAX_DURATION = 30 days;
    uint256 constant PROOF_INTERVAL = 10 hours;
    
    event DealCreated(address indexed client, address indexed server, uint256 amount, uint256 duration);
    event ProofSubmitted(address indexed server, address indexed client, uint256 timestamp);
    event DealCompleted(address indexed client, address indexed server, uint256 amount);
    event Deposit(address indexed user, uint256 amount);
    event Withdrawal(address indexed user, uint256 amount);
    
    receive() external payable {}
    
    modifier sufficientBalance(uint256 amount) {
        require(balance[msg.sender] >= amount, "Insufficient balance, BROKE CHIGGA");
        _;
    }
    
    modifier validDuration(uint256 duration) {
        require(duration <= MAX_DURATION, "Duration exceeds maximum limit, DYSLEXIC CHIGGA");
        _;
    }
    

    function deposit() external payable {
        balance[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }
    

    function withdraw(uint256 amount) external sufficientBalance(amount) {
        balance[msg.sender] -= amount;
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Transfer failed, FAILED CHIGGA");
        emit Withdrawal(msg.sender, amount);
    }
    

    function makeDeal(
        address client,
        address server,
        uint256 tokens,
        uint256 duration
    ) public payable validDuration(duration) {
        require(msg.sender == client, "Only client can initiate deal, FUCK YOU CHIGGA");
        require(balance[client] >= tokens, "Insufficient balance, CLIENT IS A BROKE CHIGGA");
        

        balance[client] -= tokens;
        deal[server][client] = tokens;
        timeOfDeal[server][client] = block.timestamp;
        dealDuration[server][client] = duration;
        lastProofTime[server][client] = block.timestamp;
        
        emit DealCreated(client, server, tokens, duration);
    }
    

    function submitProof(address client) external {
        require(deal[msg.sender][client] > 0, "No active deal found");
        require(
            block.timestamp <= timeOfDeal[msg.sender][client] + dealDuration[msg.sender][client],
            "Deal has expired"
        );
        require(
            block.timestamp >= lastProofTime[msg.sender][client] + PROOF_INTERVAL,
            "Too early for next proof"
        );
        
        lastProofTime[msg.sender][client] = block.timestamp;
        emit ProofSubmitted(msg.sender, client, block.timestamp);
    }
    

    function completeDeal(address client, address server) external {
        require(deal[server][client] > 0, "No active deal found");
        uint256 dealAmount = deal[server][client];
        uint256 dealEndTime = timeOfDeal[server][client] + dealDuration[server][client];
        

        if (block.timestamp >= dealEndTime) {
            if (lastProofTime[server][client] + PROOF_INTERVAL >= dealEndTime) {
                balance[server] += dealAmount;
            } else {
                balance[client] += dealAmount;
            }
            deal[server][client] = 0;
            timeOfDeal[server][client] = 0;
            dealDuration[server][client] = 0;
            lastProofTime[server][client] = 0;
            
            emit DealCompleted(client, server, dealAmount);
        }
    }
    
    function getDealAmount(address server, address client) external view returns (uint256) {
        return deal[server][client];
    }
    
    function getDealTimeRemaining(address server, address client) external view returns (uint256) {
        if (deal[server][client] == 0) return 0;
        uint256 endTime = timeOfDeal[server][client] + dealDuration[server][client];
        if (block.timestamp >= endTime) return 0;
        return endTime - block.timestamp;
    }
    
    function getBalance(address user) external view returns (uint256) {
        return balance[user];
    }
}
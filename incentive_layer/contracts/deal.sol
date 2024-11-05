//MIT Licensed[soon]: Feel free to use for anything!
pragma solidity ^0.8.0;

contract ContractorFileStorage {
    constructor(){}
    struct FileData {
        address payable client;
        address payable storageProvider;
        uint256 startTime;
        uint256 duration; // in hours, max 30 days (720 hours)
        uint256 storageSpace; // in bytes
        uint256 totalAmount;
        uint256 remainingAmount;
        uint256 lastValidationTime;
        bool isActive;
        bool isApproved;
    }

    // Constants
    uint256 public constant MAX_DURATION = 720 hours; // 30 days
    uint256 public constant VALIDATION_INTERVAL = 2 ; // blocks
    uint256 public constant PRICE_PER_GB_PER_HOUR = 0.0001 ether;

    // Storage
    // FileID=>FileData
    mapping(bytes32 => FileData) public files;
    receive() external payable {}
    fallback() external payable {}
    // Events
    event DealProposed(bytes32 indexed fileId, address indexed client, uint256 space, uint256 duration);
    event DealApproved(bytes32 indexed fileId, address indexed storageProvider);
    event ProofValidated(bytes32 indexed fileId, uint256 timestamp);
    event DealInvalidated(bytes32 indexed fileId, string reason);
    event DealCompleted(bytes32 indexed fileId);

    modifier onlyClient(bytes32 fileId) {
        require(files[fileId].client == msg.sender, ";;onlyClient;; : Only client can call this");
        _;
    }

    modifier dealActive(bytes32 fileId) {
        require(files[fileId].isActive, ";;dealActive;; : Deal is not active");
        _;
    }

    function proposeDeal(
        bytes32 fileId,
        uint256 storageSpace,
        uint256 durationHours
    ) external payable {
        require(durationHours <= MAX_DURATION, "[proposeDeal]: Duration exceeds maximum limit");
        require(storageSpace > 0, "[proposeDeal]: Storage space must be positive");
        require(files[fileId].client == address(0), "[proposeDeal]: File ID already exists");

        uint256 totalAmount = calculateTotalAmount(storageSpace, durationHours);

        files[fileId] =  FileData({
            client: payable(msg.sender),
            storageProvider: payable(address(0)),
            startTime: 0,
            duration: durationHours,
            storageSpace: storageSpace,
            totalAmount: totalAmount,
            remainingAmount: totalAmount,
            lastValidationTime: 0,
            isActive: false,
            isApproved: false
        });

        emit DealProposed(fileId, msg.sender, storageSpace, durationHours);
    }

    function approveDeal(bytes32 fileId, uint256 billingAmount) external payable {
//        FileData storage file = files[fileId];
        require(!files[fileId].isApproved, "[approveDeal]: Deal already approved");
        require(files[fileId].client != address(0), "[approveDeal]: Deal does not exist");
        require(billingAmount==files[fileId].totalAmount, "[approveDeal]: Mismatch between two prices!");

        files[fileId].storageProvider = payable(msg.sender);
        files[fileId].startTime = block.number;
        files[fileId].lastValidationTime = block.number;
        files[fileId].isActive = true;
        files[fileId].isApproved = true;

        emit DealApproved(fileId, msg.sender);
    }


    function validateProof(bytes32 fileId) external payable onlyClient(fileId) dealActive(fileId) {
//        FileData storage file = files[fileId];

        require(block.number >= files[fileId].lastValidationTime, "[validateProof]: Too early for validation");

        uint256 payment = 1;
        files[fileId].remainingAmount -= payment;
        files[fileId].lastValidationTime = block.number;

        payable(files[fileId].client).transfer(payment);

        emit ProofValidated(fileId, block.timestamp);

//        if (block.number >= files[fileId].startTime + (files[fileId].duration * VALIDATION_INTERVAL)) {
//            completeDeal(fileId);
//        }
    }

    function invalidateDeal(bytes32 fileId, string memory reason) external payable onlyClient(fileId) dealActive(fileId) {
//        FileData storage file = files[fileId];
//
        payable(files[fileId].client).transfer(1 );

//        files[fileId].isActive = false;
        emit DealInvalidated(fileId, reason);
    }

    function completeDeal(bytes32 fileId) internal {
        FileData storage file = files[fileId];
        file.isActive = false;

        if (file.remainingAmount > 0) {
            payable(file.storageProvider).transfer(file.remainingAmount);
        }
        delete files[fileId];

        emit DealCompleted(fileId);
    }

    function calculateTotalAmount(uint256 storageSpace, uint256 durationHours) public pure returns (uint256) {
        uint256 spaceInGB = (storageSpace + 1024 * 1024 * 1024 - 1) / (1024 * 1024 * 1024);
        return spaceInGB * durationHours * PRICE_PER_GB_PER_HOUR;
    }

    function calculatePaymentForInterval(uint256 totalAmount, uint256 totalHours) public pure returns (uint256) {
        return totalAmount;
    }
    function getFileData(bytes32 fileId) public view returns (FileData memory) {
    return files[fileId];  // Return the FileData struct for the given fileId
    }
}
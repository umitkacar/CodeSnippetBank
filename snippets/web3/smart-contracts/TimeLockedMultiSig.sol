// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title TimeLockedMultiSig
 * @dev Multisig wallet with timelock for enhanced security
 */
contract TimeLockedMultiSig {
    event TransactionProposed(uint256 indexed txId, address indexed proposer);
    event TransactionConfirmed(uint256 indexed txId, address indexed confirmer);
    event TransactionExecuted(uint256 indexed txId);
    event TransactionCanceled(uint256 indexed txId);

    uint256 public constant TIMELOCK_DURATION = 2 days;
    uint256 public constant GRACE_PERIOD = 7 days;

    address[] public owners;
    mapping(address => bool) public isOwner;
    uint256 public requiredConfirmations;

    struct Transaction {
        address to;
        uint256 value;
        bytes data;
        uint256 proposedAt;
        uint256 confirmations;
        bool executed;
        bool canceled;
        mapping(address => bool) isConfirmed;
    }

    mapping(uint256 => Transaction) public transactions;
    uint256 public txCount;

    modifier onlyOwner() {
        require(isOwner[msg.sender], "Not owner");
        _;
    }

    constructor(address[] memory _owners, uint256 _requiredConfirmations) {
        require(_owners.length >= _requiredConfirmations, "Invalid confirmations");
        require(_requiredConfirmations > 0, "Need at least 1 confirmation");

        for (uint256 i = 0; i < _owners.length; i++) {
            address owner = _owners[i];
            require(owner != address(0), "Invalid owner");
            require(!isOwner[owner], "Duplicate owner");

            isOwner[owner] = true;
            owners.push(owner);
        }

        requiredConfirmations = _requiredConfirmations;
    }

    receive() external payable {}

    function proposeTransaction(
        address _to,
        uint256 _value,
        bytes memory _data
    ) external onlyOwner returns (uint256) {
        uint256 txId = txCount++;

        Transaction storage txn = transactions[txId];
        txn.to = _to;
        txn.value = _value;
        txn.data = _data;
        txn.proposedAt = block.timestamp;
        txn.confirmations = 0;
        txn.executed = false;
        txn.canceled = false;

        emit TransactionProposed(txId, msg.sender);
        return txId;
    }

    function confirmTransaction(uint256 _txId) external onlyOwner {
        Transaction storage txn = transactions[_txId];
        require(!txn.executed, "Already executed");
        require(!txn.canceled, "Transaction canceled");
        require(!txn.isConfirmed[msg.sender], "Already confirmed");

        txn.isConfirmed[msg.sender] = true;
        txn.confirmations++;

        emit TransactionConfirmed(_txId, msg.sender);
    }

    function executeTransaction(uint256 _txId) external onlyOwner {
        Transaction storage txn = transactions[_txId];

        require(!txn.executed, "Already executed");
        require(!txn.canceled, "Transaction canceled");
        require(txn.confirmations >= requiredConfirmations, "Insufficient confirmations");
        require(
            block.timestamp >= txn.proposedAt + TIMELOCK_DURATION,
            "Timelock not passed"
        );
        require(
            block.timestamp <= txn.proposedAt + TIMELOCK_DURATION + GRACE_PERIOD,
            "Grace period expired"
        );

        txn.executed = true;

        (bool success, ) = txn.to.call{value: txn.value}(txn.data);
        require(success, "Transaction failed");

        emit TransactionExecuted(_txId);
    }

    function cancelTransaction(uint256 _txId) external onlyOwner {
        Transaction storage txn = transactions[_txId];

        require(!txn.executed, "Already executed");
        require(!txn.canceled, "Already canceled");

        txn.canceled = true;
        emit TransactionCanceled(_txId);
    }

    function getTransactionInfo(
        uint256 _txId
    )
        external
        view
        returns (
            address to,
            uint256 value,
            bytes memory data,
            uint256 proposedAt,
            uint256 confirmations,
            bool executed,
            bool canceled
        )
    {
        Transaction storage txn = transactions[_txId];
        return (
            txn.to,
            txn.value,
            txn.data,
            txn.proposedAt,
            txn.confirmations,
            txn.executed,
            txn.canceled
        );
    }

    function canExecute(uint256 _txId) external view returns (bool) {
        Transaction storage txn = transactions[_txId];

        return
            !txn.executed &&
            !txn.canceled &&
            txn.confirmations >= requiredConfirmations &&
            block.timestamp >= txn.proposedAt + TIMELOCK_DURATION &&
            block.timestamp <= txn.proposedAt + TIMELOCK_DURATION + GRACE_PERIOD;
    }
}

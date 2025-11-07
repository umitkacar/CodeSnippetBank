// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Snapshot.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ERC20Snapshot
 * @dev ERC20 with snapshot capability for voting and dividends
 */
contract ERC20SnapshotToken is ERC20, ERC20Snapshot, Ownable {
    mapping(uint256 => uint256) public snapshotTimestamps;
    uint256 public currentSnapshotId;

    event SnapshotCreated(uint256 indexed snapshotId, uint256 timestamp);

    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply
    ) ERC20(name, symbol) Ownable(msg.sender) {
        _mint(msg.sender, initialSupply);
    }

    function snapshot() external onlyOwner returns (uint256) {
        uint256 snapshotId = _snapshot();
        snapshotTimestamps[snapshotId] = block.timestamp;
        currentSnapshotId = snapshotId;
        emit SnapshotCreated(snapshotId, block.timestamp);
        return snapshotId;
    }

    function balanceOfAt(
        address account,
        uint256 snapshotId
    ) public view returns (uint256) {
        return super.balanceOfAt(account, snapshotId);
    }

    function totalSupplyAt(uint256 snapshotId) public view returns (uint256) {
        return super.totalSupplyAt(snapshotId);
    }

    function getSnapshotTimestamp(uint256 snapshotId) external view returns (uint256) {
        return snapshotTimestamps[snapshotId];
    }

    // Override required by Solidity
    function _update(
        address from,
        address to,
        uint256 value
    ) internal virtual override(ERC20, ERC20Snapshot) {
        super._update(from, to, value);
    }
}

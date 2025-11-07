// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title PausableContract
 * @dev Contract with emergency pause functionality
 */
contract PausableContract is Pausable, Ownable {
    uint256 public value;
    uint256 public pauseCount;

    event ValueSet(uint256 newValue);
    event EmergencyActionTaken(string action);

    constructor() Ownable(msg.sender) {}

    function setValue(uint256 newValue) external whenNotPaused {
        value = newValue;
        emit ValueSet(newValue);
    }

    function pause() external onlyOwner {
        _pause();
        pauseCount++;
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function emergencyAction() external onlyOwner whenPaused {
        // Emergency actions can only be taken when paused
        emit EmergencyActionTaken("emergency_action");
    }

    function getValue() external view returns (uint256) {
        return value;
    }
}

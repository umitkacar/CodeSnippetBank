// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable2Step.sol";

/**
 * @title Ownable2StepContract
 * @dev Two-step ownership transfer for added security
 */
contract Ownable2StepContract is Ownable2Step {
    uint256 public value;

    event ValueUpdated(uint256 oldValue, uint256 newValue);

    constructor() Ownable(msg.sender) {}

    function setValue(uint256 newValue) external onlyOwner {
        uint256 oldValue = value;
        value = newValue;
        emit ValueUpdated(oldValue, newValue);
    }

    function getValue() external view returns (uint256) {
        return value;
    }
}

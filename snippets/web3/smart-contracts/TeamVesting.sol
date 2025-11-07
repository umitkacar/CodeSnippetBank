// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TeamVesting
 * @dev Team token vesting with 1-year cliff and 4-year linear vesting
 */
contract TeamVesting is Ownable {
    using SafeERC20 for IERC20;

    IERC20 public immutable token;

    uint256 public constant CLIFF_DURATION = 365 days;
    uint256 public constant VESTING_DURATION = 1460 days; // 4 years
    uint256 public immutable startTime;

    struct Allocation {
        uint256 totalAmount;
        uint256 released;
    }

    mapping(address => Allocation) public allocations;
    uint256 public totalAllocated;

    event AllocationCreated(address indexed beneficiary, uint256 amount);
    event TokensReleased(address indexed beneficiary, uint256 amount);
    event AllocationTransferred(address indexed from, address indexed to, uint256 amount);

    constructor(address _token, uint256 _startTime) Ownable(msg.sender) {
        token = IERC20(_token);
        startTime = _startTime > 0 ? _startTime : block.timestamp;
    }

    function createAllocations(
        address[] calldata beneficiaries,
        uint256[] calldata amounts
    ) external onlyOwner {
        require(beneficiaries.length == amounts.length, "Length mismatch");

        uint256 total = 0;
        for (uint256 i = 0; i < beneficiaries.length; i++) {
            require(beneficiaries[i] != address(0), "Invalid address");
            require(amounts[i] > 0, "Amount must be > 0");
            require(allocations[beneficiaries[i]].totalAmount == 0, "Already allocated");

            allocations[beneficiaries[i]] = Allocation({
                totalAmount: amounts[i],
                released: 0
            });

            total += amounts[i];
            emit AllocationCreated(beneficiaries[i], amounts[i]);
        }

        totalAllocated += total;
        token.safeTransferFrom(msg.sender, address(this), total);
    }

    function release() external {
        Allocation storage allocation = allocations[msg.sender];
        require(allocation.totalAmount > 0, "No allocation");

        uint256 releasable = _releasableAmount(allocation);
        require(releasable > 0, "No tokens to release");

        allocation.released += releasable;
        token.safeTransfer(msg.sender, releasable);

        emit TokensReleased(msg.sender, releasable);
    }

    function transferAllocation(address newBeneficiary) external {
        require(newBeneficiary != address(0), "Invalid address");
        require(allocations[newBeneficiary].totalAmount == 0, "Already has allocation");

        Allocation memory allocation = allocations[msg.sender];
        require(allocation.totalAmount > 0, "No allocation");

        uint256 remaining = allocation.totalAmount - allocation.released;

        allocations[newBeneficiary] = Allocation({
            totalAmount: remaining,
            released: 0
        });

        delete allocations[msg.sender];

        emit AllocationTransferred(msg.sender, newBeneficiary, remaining);
    }

    function releasableAmount(address beneficiary) external view returns (uint256) {
        return _releasableAmount(allocations[beneficiary]);
    }

    function _releasableAmount(Allocation memory allocation) private view returns (uint256) {
        return _vestedAmount(allocation) - allocation.released;
    }

    function _vestedAmount(Allocation memory allocation) private view returns (uint256) {
        if (block.timestamp < startTime + CLIFF_DURATION) {
            return 0;
        } else if (block.timestamp >= startTime + VESTING_DURATION) {
            return allocation.totalAmount;
        } else {
            uint256 timeFromStart = block.timestamp - startTime;
            return (allocation.totalAmount * timeFromStart) / VESTING_DURATION;
        }
    }

    function getProgress() external view returns (uint256) {
        if (block.timestamp < startTime + CLIFF_DURATION) {
            return 0;
        } else if (block.timestamp >= startTime + VESTING_DURATION) {
            return 100;
        } else {
            uint256 timeFromStart = block.timestamp - startTime;
            return (timeFromStart * 100) / VESTING_DURATION;
        }
    }
}

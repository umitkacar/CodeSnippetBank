// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title VestingSchedule
 * @dev Multi-beneficiary vesting with milestone releases
 */
contract VestingScheduleAdvanced is Ownable {
    using SafeERC20 for IERC20;

    IERC20 public immutable token;

    struct Milestone {
        uint256 timestamp;
        uint256 percentage; // basis points (10000 = 100%)
    }

    struct Schedule {
        uint256 totalAmount;
        uint256 released;
        Milestone[] milestones;
        bool active;
    }

    mapping(address => Schedule) public schedules;

    event ScheduleCreated(address indexed beneficiary, uint256 amount);
    event MilestoneAdded(address indexed beneficiary, uint256 timestamp, uint256 percentage);
    event TokensReleased(address indexed beneficiary, uint256 amount);

    constructor(address _token) Ownable(msg.sender) {
        token = IERC20(_token);
    }

    function createSchedule(
        address beneficiary,
        uint256 amount,
        uint256[] calldata timestamps,
        uint256[] calldata percentages
    ) external onlyOwner {
        require(beneficiary != address(0), "Invalid beneficiary");
        require(amount > 0, "Amount must be > 0");
        require(timestamps.length == percentages.length, "Length mismatch");
        require(!schedules[beneficiary].active, "Schedule exists");

        uint256 totalPercentage = 0;
        for (uint256 i = 0; i < percentages.length; i++) {
            totalPercentage += percentages[i];
        }
        require(totalPercentage == 10000, "Percentages must sum to 100%");

        Schedule storage schedule = schedules[beneficiary];
        schedule.totalAmount = amount;
        schedule.released = 0;
        schedule.active = true;

        for (uint256 i = 0; i < timestamps.length; i++) {
            schedule.milestones.push(Milestone({
                timestamp: timestamps[i],
                percentage: percentages[i]
            }));
        }

        token.safeTransferFrom(msg.sender, address(this), amount);
        emit ScheduleCreated(beneficiary, amount);
    }

    function release() external {
        Schedule storage schedule = schedules[msg.sender];
        require(schedule.active, "No active schedule");

        uint256 releasable = _releasableAmount(msg.sender);
        require(releasable > 0, "No tokens to release");

        schedule.released += releasable;
        token.safeTransfer(msg.sender, releasable);

        emit TokensReleased(msg.sender, releasable);
    }

    function releasableAmount(address beneficiary) external view returns (uint256) {
        return _releasableAmount(beneficiary);
    }

    function _releasableAmount(address beneficiary) private view returns (uint256) {
        Schedule storage schedule = schedules[beneficiary];
        if (!schedule.active) return 0;

        uint256 vested = 0;
        for (uint256 i = 0; i < schedule.milestones.length; i++) {
            if (block.timestamp >= schedule.milestones[i].timestamp) {
                vested += (schedule.totalAmount * schedule.milestones[i].percentage) / 10000;
            }
        }

        return vested - schedule.released;
    }

    function getMilestones(address beneficiary) external view returns (Milestone[] memory) {
        return schedules[beneficiary].milestones;
    }
}

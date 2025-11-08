// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title LiquidityStaking
 * @dev Stake LP tokens to earn rewards with time-weighted bonuses
 */
contract LiquidityStaking is ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;

    IERC20 public immutable lpToken;
    IERC20 public immutable rewardToken;

    uint256 public rewardRate = 100 ether; // per second
    uint256 public totalStaked;
    uint256 public lastUpdateTime;
    uint256 public rewardPerTokenStored;

    // Time-based multipliers (basis points)
    uint256 public constant MONTH_1_MULTIPLIER = 10000;  // 1x
    uint256 public constant MONTH_3_MULTIPLIER = 15000;  // 1.5x
    uint256 public constant MONTH_6_MULTIPLIER = 20000;  // 2x
    uint256 public constant MONTH_12_MULTIPLIER = 30000; // 3x

    struct StakeInfo {
        uint256 amount;
        uint256 stakedAt;
        uint256 rewardPerTokenPaid;
        uint256 rewards;
        uint256 lockPeriod; // 0, 30, 90, 180, 365 days
    }

    mapping(address => StakeInfo) public stakes;

    event Staked(address indexed user, uint256 amount, uint256 lockPeriod);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardPaid(address indexed user, uint256 reward);

    constructor(
        address _lpToken,
        address _rewardToken
    ) Ownable(msg.sender) {
        lpToken = IERC20(_lpToken);
        rewardToken = IERC20(_rewardToken);
        lastUpdateTime = block.timestamp;
    }

    modifier updateReward(address account) {
        rewardPerTokenStored = rewardPerToken();
        lastUpdateTime = block.timestamp;

        if (account != address(0)) {
            StakeInfo storage userStake = stakes[account];
            userStake.rewards = earned(account);
            userStake.rewardPerTokenPaid = rewardPerTokenStored;
        }
        _;
    }

    function stake(uint256 amount, uint256 lockDays) external nonReentrant updateReward(msg.sender) {
        require(amount > 0, "Cannot stake 0");
        require(
            lockDays == 0 || lockDays == 30 || lockDays == 90 ||
            lockDays == 180 || lockDays == 365,
            "Invalid lock period"
        );
        require(stakes[msg.sender].amount == 0, "Already staking");

        totalStaked += amount;
        stakes[msg.sender] = StakeInfo({
            amount: amount,
            stakedAt: block.timestamp,
            rewardPerTokenPaid: rewardPerTokenStored,
            rewards: 0,
            lockPeriod: lockDays * 1 days
        });

        lpToken.safeTransferFrom(msg.sender, address(this), amount);
        emit Staked(msg.sender, amount, lockDays);
    }

    function withdraw() external nonReentrant updateReward(msg.sender) {
        StakeInfo storage userStake = stakes[msg.sender];
        require(userStake.amount > 0, "No stake");
        require(
            block.timestamp >= userStake.stakedAt + userStake.lockPeriod,
            "Still locked"
        );

        uint256 amount = userStake.amount;
        totalStaked -= amount;

        uint256 reward = userStake.rewards;
        delete stakes[msg.sender];

        lpToken.safeTransfer(msg.sender, amount);

        if (reward > 0) {
            rewardToken.safeTransfer(msg.sender, reward);
            emit RewardPaid(msg.sender, reward);
        }

        emit Withdrawn(msg.sender, amount);
    }

    function claimReward() external nonReentrant updateReward(msg.sender) {
        uint256 reward = stakes[msg.sender].rewards;
        require(reward > 0, "No reward");

        stakes[msg.sender].rewards = 0;
        rewardToken.safeTransfer(msg.sender, reward);
        emit RewardPaid(msg.sender, reward);
    }

    function rewardPerToken() public view returns (uint256) {
        if (totalStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored +
            (((block.timestamp - lastUpdateTime) * rewardRate * 1e18) / totalStaked);
    }

    function earned(address account) public view returns (uint256) {
        StakeInfo memory userStake = stakes[account];
        uint256 baseReward = ((userStake.amount *
            (rewardPerToken() - userStake.rewardPerTokenPaid)) / 1e18) +
            userStake.rewards;

        // Apply time-based multiplier
        uint256 multiplier = getMultiplier(userStake.lockPeriod);
        return (baseReward * multiplier) / 10000;
    }

    function getMultiplier(uint256 lockPeriod) public pure returns (uint256) {
        if (lockPeriod >= 365 days) return MONTH_12_MULTIPLIER;
        if (lockPeriod >= 180 days) return MONTH_6_MULTIPLIER;
        if (lockPeriod >= 90 days) return MONTH_3_MULTIPLIER;
        return MONTH_1_MULTIPLIER;
    }

    function setRewardRate(uint256 _rewardRate) external onlyOwner updateReward(address(0)) {
        rewardRate = _rewardRate;
    }
}

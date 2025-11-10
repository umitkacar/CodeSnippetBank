// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title NFTStaking
 * @dev Stake NFTs to earn ERC20 rewards
 */
contract NFTStaking is ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;

    IERC721 public immutable nftCollection;
    IERC20 public immutable rewardToken;

    uint256 public rewardPerDay = 10 ether;
    uint256 public constant SECONDS_PER_DAY = 86400;

    struct StakeInfo {
        address owner;
        uint256 stakedAt;
        uint256 lastClaimTime;
    }

    mapping(uint256 => StakeInfo) public stakedNFTs;
    mapping(address => uint256[]) public userStakedTokens;

    event NFTStaked(address indexed user, uint256 indexed tokenId);
    event NFTUnstaked(address indexed user, uint256 indexed tokenId);
    event RewardsClaimed(address indexed user, uint256 amount);

    constructor(
        address _nftCollection,
        address _rewardToken
    ) Ownable(msg.sender) {
        nftCollection = IERC721(_nftCollection);
        rewardToken = IERC20(_rewardToken);
    }

    function stake(uint256[] calldata tokenIds) external nonReentrant {
        for (uint256 i = 0; i < tokenIds.length; i++) {
            uint256 tokenId = tokenIds[i];
            require(
                nftCollection.ownerOf(tokenId) == msg.sender,
                "Not token owner"
            );

            nftCollection.transferFrom(msg.sender, address(this), tokenId);

            stakedNFTs[tokenId] = StakeInfo({
                owner: msg.sender,
                stakedAt: block.timestamp,
                lastClaimTime: block.timestamp
            });

            userStakedTokens[msg.sender].push(tokenId);
            emit NFTStaked(msg.sender, tokenId);
        }
    }

    function unstake(uint256[] calldata tokenIds) external nonReentrant {
        uint256 totalReward = 0;

        for (uint256 i = 0; i < tokenIds.length; i++) {
            uint256 tokenId = tokenIds[i];
            require(stakedNFTs[tokenId].owner == msg.sender, "Not token owner");

            uint256 reward = calculateReward(tokenId);
            totalReward += reward;

            nftCollection.transferFrom(address(this), msg.sender, tokenId);

            _removeTokenFromUser(msg.sender, tokenId);
            delete stakedNFTs[tokenId];

            emit NFTUnstaked(msg.sender, tokenId);
        }

        if (totalReward > 0) {
            rewardToken.safeTransfer(msg.sender, totalReward);
            emit RewardsClaimed(msg.sender, totalReward);
        }
    }

    function claimRewards(uint256[] calldata tokenIds) external nonReentrant {
        uint256 totalReward = 0;

        for (uint256 i = 0; i < tokenIds.length; i++) {
            uint256 tokenId = tokenIds[i];
            require(stakedNFTs[tokenId].owner == msg.sender, "Not token owner");

            uint256 reward = calculateReward(tokenId);
            totalReward += reward;

            stakedNFTs[tokenId].lastClaimTime = block.timestamp;
        }

        require(totalReward > 0, "No rewards");
        rewardToken.safeTransfer(msg.sender, totalReward);
        emit RewardsClaimed(msg.sender, totalReward);
    }

    function calculateReward(uint256 tokenId) public view returns (uint256) {
        StakeInfo memory info = stakedNFTs[tokenId];
        if (info.owner == address(0)) return 0;

        uint256 timeStaked = block.timestamp - info.lastClaimTime;
        return (timeStaked * rewardPerDay) / SECONDS_PER_DAY;
    }

    function getUserStakedTokens(address user) external view returns (uint256[] memory) {
        return userStakedTokens[user];
    }

    function setRewardPerDay(uint256 _rewardPerDay) external onlyOwner {
        rewardPerDay = _rewardPerDay;
    }

    function _removeTokenFromUser(address user, uint256 tokenId) private {
        uint256[] storage tokens = userStakedTokens[user];
        for (uint256 i = 0; i < tokens.length; i++) {
            if (tokens[i] == tokenId) {
                tokens[i] = tokens[tokens.length - 1];
                tokens.pop();
                break;
            }
        }
    }
}

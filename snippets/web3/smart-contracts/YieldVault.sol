// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title YieldVault
 * @dev Yield-generating vault with strategy integration
 */
contract YieldVault is ERC20, ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;

    IERC20 public immutable asset;

    uint256 public totalAssets;
    uint256 public performanceFee = 1000; // 10%
    uint256 public constant MAX_FEE = 2000; // 20% max
    uint256 public constant BASIS_POINTS = 10000;

    address public treasury;
    uint256 public lastHarvestTimestamp;

    event Deposit(address indexed user, uint256 assets, uint256 shares);
    event Withdraw(address indexed user, uint256 assets, uint256 shares);
    event Harvest(uint256 profit, uint256 fee);

    constructor(
        address _asset,
        string memory _name,
        string memory _symbol,
        address _treasury
    ) ERC20(_name, _symbol) Ownable(msg.sender) {
        asset = IERC20(_asset);
        treasury = _treasury;
        lastHarvestTimestamp = block.timestamp;
    }

    function deposit(uint256 assets) external nonReentrant returns (uint256 shares) {
        require(assets > 0, "Cannot deposit 0");

        shares = totalSupply() == 0
            ? assets
            : (assets * totalSupply()) / totalAssets;

        asset.safeTransferFrom(msg.sender, address(this), assets);

        _mint(msg.sender, shares);
        totalAssets += assets;

        emit Deposit(msg.sender, assets, shares);
    }

    function withdraw(uint256 shares) external nonReentrant returns (uint256 assets) {
        require(shares > 0, "Cannot withdraw 0");
        require(balanceOf(msg.sender) >= shares, "Insufficient balance");

        assets = (shares * totalAssets) / totalSupply();

        _burn(msg.sender, shares);
        totalAssets -= assets;

        asset.safeTransfer(msg.sender, assets);

        emit Withdraw(msg.sender, assets, shares);
    }

    function harvest(uint256 profit) external onlyOwner {
        require(profit > 0, "No profit");

        uint256 fee = (profit * performanceFee) / BASIS_POINTS;
        uint256 netProfit = profit - fee;

        totalAssets += netProfit;

        if (fee > 0) {
            asset.safeTransfer(treasury, fee);
        }

        lastHarvestTimestamp = block.timestamp;
        emit Harvest(profit, fee);
    }

    function previewDeposit(uint256 assets) external view returns (uint256) {
        return totalSupply() == 0
            ? assets
            : (assets * totalSupply()) / totalAssets;
    }

    function previewWithdraw(uint256 shares) external view returns (uint256) {
        return (shares * totalAssets) / totalSupply();
    }

    function setPerformanceFee(uint256 _fee) external onlyOwner {
        require(_fee <= MAX_FEE, "Fee too high");
        performanceFee = _fee;
    }

    function setTreasury(address _treasury) external onlyOwner {
        require(_treasury != address(0), "Invalid address");
        treasury = _treasury;
    }

    function getPricePerShare() external view returns (uint256) {
        return totalSupply() == 0 ? 1e18 : (totalAssets * 1e18) / totalSupply();
    }
}

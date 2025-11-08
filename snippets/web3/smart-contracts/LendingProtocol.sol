// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title LendingProtocol
 * @dev Simple lending and borrowing protocol
 */
contract LendingProtocol is ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;

    struct Market {
        IERC20 token;
        uint256 totalDeposits;
        uint256 totalBorrows;
        uint256 borrowRate; // Annual rate in basis points
        uint256 collateralFactor; // In basis points (7500 = 75%)
    }

    struct UserPosition {
        uint256 deposited;
        uint256 borrowed;
        uint256 lastUpdateTime;
    }

    mapping(address => Market) public markets;
    mapping(address => mapping(address => UserPosition)) public positions;

    address[] public supportedTokens;

    uint256 public constant SECONDS_PER_YEAR = 31536000;
    uint256 public constant BASIS_POINTS = 10000;

    event Deposit(address indexed user, address indexed token, uint256 amount);
    event Withdraw(address indexed user, address indexed token, uint256 amount);
    event Borrow(address indexed user, address indexed token, uint256 amount);
    event Repay(address indexed user, address indexed token, uint256 amount);
    event MarketAdded(address indexed token, uint256 borrowRate, uint256 collateralFactor);

    constructor() Ownable(msg.sender) {}

    function addMarket(
        address token,
        uint256 borrowRate,
        uint256 collateralFactor
    ) external onlyOwner {
        require(address(markets[token].token) == address(0), "Market exists");
        require(collateralFactor <= BASIS_POINTS, "Invalid collateral factor");

        markets[token] = Market({
            token: IERC20(token),
            totalDeposits: 0,
            totalBorrows: 0,
            borrowRate: borrowRate,
            collateralFactor: collateralFactor
        });

        supportedTokens.push(token);
        emit MarketAdded(token, borrowRate, collateralFactor);
    }

    function deposit(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        require(address(market.token) != address(0), "Market not found");

        _accrueInterest(token, msg.sender);

        market.token.safeTransferFrom(msg.sender, address(this), amount);
        market.totalDeposits += amount;
        positions[token][msg.sender].deposited += amount;

        emit Deposit(msg.sender, token, amount);
    }

    function withdraw(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        UserPosition storage position = positions[token][msg.sender];

        require(position.deposited >= amount, "Insufficient balance");
        _accrueInterest(token, msg.sender);

        require(_isHealthy(msg.sender), "Unhealthy position");

        position.deposited -= amount;
        market.totalDeposits -= amount;

        market.token.safeTransfer(msg.sender, amount);
        emit Withdraw(msg.sender, token, amount);
    }

    function borrow(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        require(address(market.token) != address(0), "Market not found");
        require(market.totalDeposits >= market.totalBorrows + amount, "Insufficient liquidity");

        _accrueInterest(token, msg.sender);

        positions[token][msg.sender].borrowed += amount;
        market.totalBorrows += amount;

        require(_isHealthy(msg.sender), "Insufficient collateral");

        market.token.safeTransfer(msg.sender, amount);
        emit Borrow(msg.sender, token, amount);
    }

    function repay(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        UserPosition storage position = positions[token][msg.sender];

        _accrueInterest(token, msg.sender);

        uint256 repayAmount = amount > position.borrowed ? position.borrowed : amount;

        market.token.safeTransferFrom(msg.sender, address(this), repayAmount);

        position.borrowed -= repayAmount;
        market.totalBorrows -= repayAmount;

        emit Repay(msg.sender, token, repayAmount);
    }

    function _accrueInterest(address token, address user) private {
        UserPosition storage position = positions[token][user];
        if (position.borrowed == 0 || position.lastUpdateTime == 0) {
            position.lastUpdateTime = block.timestamp;
            return;
        }

        uint256 timeElapsed = block.timestamp - position.lastUpdateTime;
        uint256 interest = (position.borrowed * markets[token].borrowRate * timeElapsed) /
            (SECONDS_PER_YEAR * BASIS_POINTS);

        position.borrowed += interest;
        position.lastUpdateTime = block.timestamp;
    }

    function _isHealthy(address user) private view returns (bool) {
        uint256 totalCollateralValue = 0;
        uint256 totalBorrowValue = 0;

        for (uint256 i = 0; i < supportedTokens.length; i++) {
            address token = supportedTokens[i];
            UserPosition storage position = positions[token][user];
            Market storage market = markets[token];

            totalCollateralValue +=
                (position.deposited * market.collateralFactor) /
                BASIS_POINTS;
            totalBorrowValue += position.borrowed;
        }

        return totalCollateralValue >= totalBorrowValue;
    }

    function getAccountHealth(address user) external view returns (uint256) {
        uint256 totalCollateralValue = 0;
        uint256 totalBorrowValue = 0;

        for (uint256 i = 0; i < supportedTokens.length; i++) {
            address token = supportedTokens[i];
            UserPosition storage position = positions[token][user];
            Market storage market = markets[token];

            totalCollateralValue +=
                (position.deposited * market.collateralFactor) /
                BASIS_POINTS;
            totalBorrowValue += position.borrowed;
        }

        if (totalBorrowValue == 0) return type(uint256).max;
        return (totalCollateralValue * BASIS_POINTS) / totalBorrowValue;
    }
}

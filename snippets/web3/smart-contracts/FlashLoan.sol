// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

interface IFlashLoanReceiver {
    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata params
    ) external returns (bool);
}

/**
 * @title FlashLoan
 * @dev Flash loan provider with fee
 */
contract FlashLoan is ReentrancyGuard {
    using SafeERC20 for IERC20;

    uint256 public constant FEE_PERCENTAGE = 9; // 0.09% fee
    uint256 public constant FEE_PRECISION = 10000;

    mapping(address => uint256) public poolBalance;

    event FlashLoan(
        address indexed borrower,
        address indexed token,
        uint256 amount,
        uint256 fee
    );
    event LiquidityAdded(address indexed provider, address indexed token, uint256 amount);
    event LiquidityRemoved(address indexed provider, address indexed token, uint256 amount);

    function addLiquidity(address token, uint256 amount) external {
        require(amount > 0, "Amount must be > 0");

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        poolBalance[token] += amount;

        emit LiquidityAdded(msg.sender, token, amount);
    }

    function removeLiquidity(address token, uint256 amount) external {
        require(amount > 0, "Amount must be > 0");
        require(poolBalance[token] >= amount, "Insufficient pool balance");

        poolBalance[token] -= amount;
        IERC20(token).safeTransfer(msg.sender, amount);

        emit LiquidityRemoved(msg.sender, token, amount);
    }

    function flashLoan(
        address token,
        uint256 amount,
        bytes calldata params
    ) external nonReentrant {
        require(amount > 0, "Amount must be > 0");
        require(poolBalance[token] >= amount, "Insufficient liquidity");

        uint256 fee = (amount * FEE_PERCENTAGE) / FEE_PRECISION;
        uint256 balanceBefore = IERC20(token).balanceOf(address(this));

        // Transfer tokens to borrower
        IERC20(token).safeTransfer(msg.sender, amount);

        // Execute borrower's logic
        require(
            IFlashLoanReceiver(msg.sender).executeOperation(
                token,
                amount,
                fee,
                params
            ),
            "Flash loan execution failed"
        );

        // Verify repayment with fee
        uint256 balanceAfter = IERC20(token).balanceOf(address(this));
        require(
            balanceAfter >= balanceBefore + fee,
            "Flash loan not repaid"
        );

        poolBalance[token] = balanceAfter;

        emit FlashLoan(msg.sender, token, amount, fee);
    }

    function getAvailableLiquidity(address token) external view returns (uint256) {
        return poolBalance[token];
    }

    function calculateFee(uint256 amount) external pure returns (uint256) {
        return (amount * FEE_PERCENTAGE) / FEE_PRECISION;
    }
}

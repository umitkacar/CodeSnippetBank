// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title LiquidityPool
 * @dev Two-token liquidity pool with LP tokens
 */
contract LiquidityPool is ERC20, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable tokenA;
    IERC20 public immutable tokenB;

    uint256 public reserveA;
    uint256 public reserveB;

    uint256 private constant MINIMUM_LIQUIDITY = 10**3;

    event LiquidityAdded(
        address indexed provider,
        uint256 amountA,
        uint256 amountB,
        uint256 liquidity
    );
    event LiquidityRemoved(
        address indexed provider,
        uint256 amountA,
        uint256 amountB,
        uint256 liquidity
    );
    event Swap(
        address indexed user,
        uint256 amountAIn,
        uint256 amountBIn,
        uint256 amountAOut,
        uint256 amountBOut
    );

    constructor(
        address _tokenA,
        address _tokenB,
        string memory lpName,
        string memory lpSymbol
    ) ERC20(lpName, lpSymbol) {
        tokenA = IERC20(_tokenA);
        tokenB = IERC20(_tokenB);
    }

    function addLiquidity(
        uint256 amountADesired,
        uint256 amountBDesired,
        uint256 amountAMin,
        uint256 amountBMin
    ) external nonReentrant returns (uint256 liquidity) {
        (uint256 amountA, uint256 amountB) = _calculateLiquidityAmounts(
            amountADesired,
            amountBDesired,
            amountAMin,
            amountBMin
        );

        tokenA.safeTransferFrom(msg.sender, address(this), amountA);
        tokenB.safeTransferFrom(msg.sender, address(this), amountB);

        uint256 _totalSupply = totalSupply();

        if (_totalSupply == 0) {
            liquidity = sqrt(amountA * amountB) - MINIMUM_LIQUIDITY;
            _mint(address(1), MINIMUM_LIQUIDITY);
        } else {
            liquidity = min(
                (amountA * _totalSupply) / reserveA,
                (amountB * _totalSupply) / reserveB
            );
        }

        require(liquidity > 0, "Insufficient liquidity minted");

        _mint(msg.sender, liquidity);
        _update(reserveA + amountA, reserveB + amountB);

        emit LiquidityAdded(msg.sender, amountA, amountB, liquidity);
    }

    function removeLiquidity(
        uint256 liquidity,
        uint256 amountAMin,
        uint256 amountBMin
    ) external nonReentrant returns (uint256 amountA, uint256 amountB) {
        require(balanceOf(msg.sender) >= liquidity, "Insufficient LP tokens");

        uint256 _totalSupply = totalSupply();
        amountA = (liquidity * reserveA) / _totalSupply;
        amountB = (liquidity * reserveB) / _totalSupply;

        require(amountA >= amountAMin, "Insufficient A amount");
        require(amountB >= amountBMin, "Insufficient B amount");

        _burn(msg.sender, liquidity);

        tokenA.safeTransfer(msg.sender, amountA);
        tokenB.safeTransfer(msg.sender, amountB);

        _update(reserveA - amountA, reserveB - amountB);

        emit LiquidityRemoved(msg.sender, amountA, amountB, liquidity);
    }

    function swap(
        uint256 amountAIn,
        uint256 amountBIn,
        uint256 amountAOutMin,
        uint256 amountBOutMin
    ) external nonReentrant {
        require(amountAIn > 0 || amountBIn > 0, "Invalid input amount");
        require(amountAIn == 0 || amountBIn == 0, "Only one input allowed");

        uint256 amountAOut;
        uint256 amountBOut;

        if (amountAIn > 0) {
            tokenA.safeTransferFrom(msg.sender, address(this), amountAIn);
            amountBOut = getAmountOut(amountAIn, reserveA, reserveB);
            require(amountBOut >= amountBOutMin, "Insufficient output amount");
            tokenB.safeTransfer(msg.sender, amountBOut);
        } else {
            tokenB.safeTransferFrom(msg.sender, address(this), amountBIn);
            amountAOut = getAmountOut(amountBIn, reserveB, reserveA);
            require(amountAOut >= amountAOutMin, "Insufficient output amount");
            tokenA.safeTransfer(msg.sender, amountAOut);
        }

        _update(
            tokenA.balanceOf(address(this)),
            tokenB.balanceOf(address(this))
        );

        emit Swap(msg.sender, amountAIn, amountBIn, amountAOut, amountBOut);
    }

    function getAmountOut(
        uint256 amountIn,
        uint256 reserveIn,
        uint256 reserveOut
    ) public pure returns (uint256) {
        require(amountIn > 0, "Insufficient input amount");
        require(reserveIn > 0 && reserveOut > 0, "Insufficient liquidity");

        uint256 amountInWithFee = amountIn * 997;
        uint256 numerator = amountInWithFee * reserveOut;
        uint256 denominator = (reserveIn * 1000) + amountInWithFee;

        return numerator / denominator;
    }

    function _calculateLiquidityAmounts(
        uint256 amountADesired,
        uint256 amountBDesired,
        uint256 amountAMin,
        uint256 amountBMin
    ) private view returns (uint256 amountA, uint256 amountB) {
        if (reserveA == 0 && reserveB == 0) {
            return (amountADesired, amountBDesired);
        }

        uint256 amountBOptimal = (amountADesired * reserveB) / reserveA;
        if (amountBOptimal <= amountBDesired) {
            require(amountBOptimal >= amountBMin, "Insufficient B amount");
            return (amountADesired, amountBOptimal);
        }

        uint256 amountAOptimal = (amountBDesired * reserveA) / reserveB;
        require(amountAOptimal <= amountADesired, "Optimal A exceeds desired");
        require(amountAOptimal >= amountAMin, "Insufficient A amount");
        return (amountAOptimal, amountBDesired);
    }

    function _update(uint256 balanceA, uint256 balanceB) private {
        reserveA = balanceA;
        reserveB = balanceB;
    }

    function sqrt(uint256 y) internal pure returns (uint256 z) {
        if (y > 3) {
            z = y;
            uint256 x = y / 2 + 1;
            while (x < z) {
                z = x;
                x = (y / x + x) / 2;
            }
        } else if (y != 0) {
            z = 1;
        }
    }

    function min(uint256 x, uint256 y) internal pure returns (uint256) {
        return x < y ? x : y;
    }
}

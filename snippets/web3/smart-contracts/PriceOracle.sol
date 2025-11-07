// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title PriceOracle
 * @dev Simple price oracle with manual updates and time-weighted average
 */
contract PriceOracle is Ownable {
    struct PriceData {
        uint256 price;
        uint256 timestamp;
    }

    mapping(address => PriceData) public prices;
    mapping(address => uint256[]) public priceHistory;

    uint256 public constant MAX_PRICE_AGE = 1 hours;
    uint256 public constant MIN_UPDATE_INTERVAL = 5 minutes;

    event PriceUpdated(address indexed token, uint256 price, uint256 timestamp);

    constructor() Ownable(msg.sender) {}

    function updatePrice(address token, uint256 price) external onlyOwner {
        require(price > 0, "Invalid price");

        PriceData storage data = prices[token];

        if (data.timestamp > 0) {
            require(
                block.timestamp >= data.timestamp + MIN_UPDATE_INTERVAL,
                "Update too frequent"
            );
        }

        data.price = price;
        data.timestamp = block.timestamp;

        priceHistory[token].push(price);
        if (priceHistory[token].length > 100) {
            // Keep only last 100 prices
            _removeOldestPrice(token);
        }

        emit PriceUpdated(token, price, block.timestamp);
    }

    function getPrice(address token) external view returns (uint256) {
        PriceData memory data = prices[token];
        require(data.timestamp > 0, "Price not set");
        require(
            block.timestamp <= data.timestamp + MAX_PRICE_AGE,
            "Price too old"
        );
        return data.price;
    }

    function getTWAP(address token, uint256 periods) external view returns (uint256) {
        uint256[] storage history = priceHistory[token];
        require(history.length >= periods, "Insufficient data");

        uint256 sum = 0;
        uint256 count = periods > history.length ? history.length : periods;

        for (uint256 i = history.length - count; i < history.length; i++) {
            sum += history[i];
        }

        return sum / count;
    }

    function _removeOldestPrice(address token) private {
        uint256[] storage history = priceHistory[token];
        for (uint256 i = 0; i < history.length - 1; i++) {
            history[i] = history[i + 1];
        }
        history.pop();
    }

    function getPriceAge(address token) external view returns (uint256) {
        return block.timestamp - prices[token].timestamp;
    }

    function isPriceValid(address token) external view returns (bool) {
        PriceData memory data = prices[token];
        return data.timestamp > 0 &&
               block.timestamp <= data.timestamp + MAX_PRICE_AGE;
    }
}

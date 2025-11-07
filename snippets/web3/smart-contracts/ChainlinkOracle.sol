// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/**
 * @title ChainlinkOracle
 * @dev Chainlink price feed integration
 */
contract ChainlinkOracle {
    mapping(address => address) public priceFeeds;

    event PriceFeedAdded(address indexed token, address indexed feed);

    function addPriceFeed(address token, address feed) external {
        require(token != address(0) && feed != address(0), "Invalid address");
        priceFeeds[token] = feed;
        emit PriceFeedAdded(token, feed);
    }

    function getLatestPrice(address token) external view returns (uint256, uint256) {
        address feedAddress = priceFeeds[token];
        require(feedAddress != address(0), "Price feed not set");

        AggregatorV3Interface priceFeed = AggregatorV3Interface(feedAddress);

        (
            uint80 roundID,
            int256 price,
            ,
            uint256 timestamp,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        require(price > 0, "Invalid price");
        require(answeredInRound >= roundID, "Stale price");
        require(timestamp > 0, "Round not complete");

        return (uint256(price), timestamp);
    }

    function getPriceDecimals(address token) external view returns (uint8) {
        address feedAddress = priceFeeds[token];
        require(feedAddress != address(0), "Price feed not set");

        return AggregatorV3Interface(feedAddress).decimals();
    }

    function getHistoricalPrice(
        address token,
        uint80 roundId
    ) external view returns (uint256, uint256) {
        address feedAddress = priceFeeds[token];
        require(feedAddress != address(0), "Price feed not set");

        AggregatorV3Interface priceFeed = AggregatorV3Interface(feedAddress);

        (
            ,
            int256 price,
            ,
            uint256 timestamp,

        ) = priceFeed.getRoundData(roundId);

        require(price > 0, "Invalid price");
        return (uint256(price), timestamp);
    }

    function isPriceStale(address token, uint256 maxAge) external view returns (bool) {
        (, uint256 timestamp) = this.getLatestPrice(token);
        return block.timestamp - timestamp > maxAge;
    }
}

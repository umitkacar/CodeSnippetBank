// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/proxy/beacon/BeaconProxy.sol";
import "@openzeppelin/contracts/proxy/beacon/UpgradeableBeacon.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title BeaconProxyFactory
 * @dev Factory for creating beacon proxies
 */
contract BeaconProxyFactory is Ownable {
    UpgradeableBeacon public immutable beacon;

    event ProxyCreated(address indexed proxy);

    constructor(address implementation) Ownable(msg.sender) {
        beacon = new UpgradeableBeacon(implementation, address(this));
    }

    function createProxy(bytes memory data) external returns (address) {
        BeaconProxy proxy = new BeaconProxy(
            address(beacon),
            data
        );
        emit ProxyCreated(address(proxy));
        return address(proxy);
    }

    function upgrade(address newImplementation) external onlyOwner {
        beacon.upgradeTo(newImplementation);
    }

    function implementation() external view returns (address) {
        return beacon.implementation();
    }
}

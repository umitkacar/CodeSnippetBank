// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/proxy/transparent/ProxyAdmin.sol";

/**
 * @title ProxyAdminContract
 * @dev Admin contract for managing transparent proxies
 */
contract ProxyAdminContract is ProxyAdmin {
    constructor(address initialOwner) ProxyAdmin(initialOwner) {}
}

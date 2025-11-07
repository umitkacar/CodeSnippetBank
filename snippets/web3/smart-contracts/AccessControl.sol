// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title RBACContract
 * @dev Role-based access control with pausable functionality
 */
contract RBACContract is AccessControl, Pausable {
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    event RoleGrantedWithExpiry(
        bytes32 indexed role,
        address indexed account,
        uint256 expiry
    );

    mapping(bytes32 => mapping(address => uint256)) public roleExpiry;

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
    }

    function grantRoleWithExpiry(
        bytes32 role,
        address account,
        uint256 duration
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _grantRole(role, account);
        roleExpiry[role][account] = block.timestamp + duration;
        emit RoleGrantedWithExpiry(role, account, block.timestamp + duration);
    }

    function hasRole(
        bytes32 role,
        address account
    ) public view override returns (bool) {
        if (!super.hasRole(role, account)) {
            return false;
        }

        uint256 expiry = roleExpiry[role][account];
        if (expiry == 0) {
            return true;
        }

        return block.timestamp <= expiry;
    }

    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    function revokeExpiredRole(
        bytes32 role,
        address account
    ) external {
        uint256 expiry = roleExpiry[role][account];
        require(expiry > 0 && block.timestamp > expiry, "Role not expired");
        _revokeRole(role, account);
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title RoleBasedAccess
 * @dev Advanced role-based access control with delegation
 */
contract RoleBasedAccess is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MODERATOR_ROLE = keccak256("MODERATOR_ROLE");
    bytes32 public constant USER_ROLE = keccak256("USER_ROLE");

    mapping(address => bool) public banned;

    event UserBanned(address indexed user);
    event UserUnbanned(address indexed user);
    event ActionPerformed(address indexed user, string action);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);

        _setRoleAdmin(MODERATOR_ROLE, ADMIN_ROLE);
        _setRoleAdmin(USER_ROLE, MODERATOR_ROLE);
    }

    modifier notBanned() {
        require(!banned[msg.sender], "User is banned");
        _;
    }

    function banUser(address user) external onlyRole(MODERATOR_ROLE) {
        banned[user] = true;
        emit UserBanned(user);
    }

    function unbanUser(address user) external onlyRole(MODERATOR_ROLE) {
        banned[user] = false;
        emit UserUnbanned(user);
    }

    function performAdminAction() external onlyRole(ADMIN_ROLE) notBanned {
        emit ActionPerformed(msg.sender, "admin_action");
    }

    function performModeratorAction() external onlyRole(MODERATOR_ROLE) notBanned {
        emit ActionPerformed(msg.sender, "moderator_action");
    }

    function performUserAction() external onlyRole(USER_ROLE) notBanned {
        emit ActionPerformed(msg.sender, "user_action");
    }

    function grantUserRole(address user) external onlyRole(MODERATOR_ROLE) {
        _grantRole(USER_ROLE, user);
    }

    function revokeUserRole(address user) external onlyRole(MODERATOR_ROLE) {
        _revokeRole(USER_ROLE, user);
    }
}

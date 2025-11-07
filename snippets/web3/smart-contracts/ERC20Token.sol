// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ERC20Token
 * @dev Production-ready ERC20 token with burn capability
 */
contract ERC20Token is ERC20, ERC20Burnable, Ownable {
    uint8 private _decimals;
    uint256 public immutable maxSupply;

    event TokensMinted(address indexed to, uint256 amount);
    event MaxSupplyReached();

    constructor(
        string memory name,
        string memory symbol,
        uint8 decimals_,
        uint256 initialSupply,
        uint256 maxSupply_
    ) ERC20(name, symbol) Ownable(msg.sender) {
        _decimals = decimals_;
        maxSupply = maxSupply_;
        _mint(msg.sender, initialSupply);
    }

    function decimals() public view virtual override returns (uint8) {
        return _decimals;
    }

    function mint(address to, uint256 amount) external onlyOwner {
        require(totalSupply() + amount <= maxSupply, "Max supply exceeded");
        _mint(to, amount);
        emit TokensMinted(to, amount);

        if (totalSupply() == maxSupply) {
            emit MaxSupplyReached();
        }
    }

    function batchTransfer(
        address[] calldata recipients,
        uint256[] calldata amounts
    ) external returns (bool) {
        require(recipients.length == amounts.length, "Length mismatch");

        for (uint256 i = 0; i < recipients.length; i++) {
            _transfer(msg.sender, recipients[i], amounts[i]);
        }

        return true;
    }
}

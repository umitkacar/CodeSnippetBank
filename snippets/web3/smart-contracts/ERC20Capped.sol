// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Capped.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ERC20CappedToken
 * @dev ERC20 with supply cap and controlled minting
 */
contract ERC20CappedToken is ERC20, ERC20Capped, Ownable {
    uint256 public mintingStartTime;
    uint256 public constant MINTING_PERIOD = 365 days;
    uint256 public lastMintTime;

    event MintingPeriodStarted(uint256 startTime);

    constructor(
        string memory name,
        string memory symbol,
        uint256 cap_,
        uint256 initialSupply
    ) ERC20(name, symbol) ERC20Capped(cap_) Ownable(msg.sender) {
        require(initialSupply <= cap_, "Initial supply exceeds cap");
        _mint(msg.sender, initialSupply);
        mintingStartTime = block.timestamp;
        lastMintTime = block.timestamp;
        emit MintingPeriodStarted(mintingStartTime);
    }

    function mint(address to, uint256 amount) external onlyOwner {
        require(
            block.timestamp >= lastMintTime + 30 days,
            "Minting too frequent"
        );
        _mint(to, amount);
        lastMintTime = block.timestamp;
    }

    function remainingSupply() external view returns (uint256) {
        return cap() - totalSupply();
    }

    function mintingProgress() external view returns (uint256) {
        return (totalSupply() * 100) / cap();
    }

    // Override required by Solidity
    function _update(
        address from,
        address to,
        uint256 value
    ) internal virtual override(ERC20, ERC20Capped) {
        super._update(from, to, value);
    }
}

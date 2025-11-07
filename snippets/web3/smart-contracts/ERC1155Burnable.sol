// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ERC1155Burnable
 * @dev Multi-token with burn functionality
 */
contract ERC1155BurnableToken is ERC1155, ERC1155Burnable, Ownable {
    string public name;
    string public symbol;

    mapping(uint256 => uint256) public totalSupply;
    mapping(uint256 => uint256) public totalBurned;

    event TokensBurned(address indexed burner, uint256 indexed tokenId, uint256 amount);
    event BatchBurned(address indexed burner, uint256[] tokenIds, uint256[] amounts);

    constructor(
        string memory _name,
        string memory _symbol,
        string memory uri
    ) ERC1155(uri) Ownable(msg.sender) {
        name = _name;
        symbol = _symbol;
    }

    function mint(address to, uint256 id, uint256 amount) external onlyOwner {
        totalSupply[id] += amount;
        _mint(to, id, amount, "");
    }

    function mintBatch(
        address to,
        uint256[] memory ids,
        uint256[] memory amounts
    ) external onlyOwner {
        for (uint256 i = 0; i < ids.length; i++) {
            totalSupply[ids[i]] += amounts[i];
        }
        _mintBatch(to, ids, amounts, "");
    }

    function burn(address account, uint256 id, uint256 amount) public override {
        super.burn(account, id, amount);
        totalBurned[id] += amount;
        emit TokensBurned(account, id, amount);
    }

    function burnBatch(
        address account,
        uint256[] memory ids,
        uint256[] memory amounts
    ) public override {
        super.burnBatch(account, ids, amounts);
        for (uint256 i = 0; i < ids.length; i++) {
            totalBurned[ids[i]] += amounts[i];
        }
        emit BatchBurned(account, ids, amounts);
    }

    function circulatingSupply(uint256 id) external view returns (uint256) {
        return totalSupply[id] - totalBurned[id];
    }
}

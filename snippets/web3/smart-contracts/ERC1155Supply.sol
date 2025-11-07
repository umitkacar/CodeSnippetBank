// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Supply.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ERC1155SupplyTracking
 * @dev Multi-token with automatic supply tracking
 */
contract ERC1155SupplyTracking is ERC1155, ERC1155Supply, Ownable {
    string public name;
    string public symbol;

    mapping(uint256 => uint256) public maxSupply;
    mapping(uint256 => bool) public tokenExists;

    constructor(
        string memory _name,
        string memory _symbol,
        string memory uri
    ) ERC1155(uri) Ownable(msg.sender) {
        name = _name;
        symbol = _symbol;
    }

    function createToken(uint256 tokenId, uint256 _maxSupply) external onlyOwner {
        require(!tokenExists[tokenId], "Token already exists");
        tokenExists[tokenId] = true;
        maxSupply[tokenId] = _maxSupply;
    }

    function mint(address to, uint256 id, uint256 amount) external onlyOwner {
        require(tokenExists[id], "Token does not exist");
        require(totalSupply(id) + amount <= maxSupply[id], "Max supply exceeded");
        _mint(to, id, amount, "");
    }

    function mintBatch(
        address to,
        uint256[] memory ids,
        uint256[] memory amounts
    ) external onlyOwner {
        for (uint256 i = 0; i < ids.length; i++) {
            require(tokenExists[ids[i]], "Token does not exist");
            require(
                totalSupply(ids[i]) + amounts[i] <= maxSupply[ids[i]],
                "Max supply exceeded"
            );
        }
        _mintBatch(to, ids, amounts, "");
    }

    function remainingSupply(uint256 id) external view returns (uint256) {
        require(tokenExists[id], "Token does not exist");
        return maxSupply[id] - totalSupply(id);
    }

    // Required override
    function _update(
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory values
    ) internal virtual override(ERC1155, ERC1155Supply) {
        super._update(from, to, ids, values);
    }
}

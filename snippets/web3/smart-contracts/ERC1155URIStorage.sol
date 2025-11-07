// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ERC1155URIStorage
 * @dev Multi-token with individual URI storage per token
 */
contract ERC1155URIStorage is ERC1155, Ownable {
    string public name;
    string public symbol;

    mapping(uint256 => string) private _tokenURIs;
    mapping(uint256 => bool) public tokenExists;

    event TokenURISet(uint256 indexed tokenId, string uri);

    constructor(
        string memory _name,
        string memory _symbol
    ) ERC1155("") Ownable(msg.sender) {
        name = _name;
        symbol = _symbol;
    }

    function createToken(
        uint256 tokenId,
        string memory tokenURI
    ) external onlyOwner {
        require(!tokenExists[tokenId], "Token already exists");
        tokenExists[tokenId] = true;
        _tokenURIs[tokenId] = tokenURI;
        emit TokenURISet(tokenId, tokenURI);
    }

    function mint(
        address to,
        uint256 id,
        uint256 amount
    ) external onlyOwner {
        require(tokenExists[id], "Token does not exist");
        _mint(to, id, amount, "");
    }

    function mintBatch(
        address to,
        uint256[] memory ids,
        uint256[] memory amounts
    ) external onlyOwner {
        for (uint256 i = 0; i < ids.length; i++) {
            require(tokenExists[ids[i]], "Token does not exist");
        }
        _mintBatch(to, ids, amounts, "");
    }

    function setTokenURI(uint256 tokenId, string memory tokenURI) external onlyOwner {
        require(tokenExists[tokenId], "Token does not exist");
        _tokenURIs[tokenId] = tokenURI;
        emit TokenURISet(tokenId, tokenURI);
    }

    function uri(uint256 tokenId) public view override returns (string memory) {
        require(tokenExists[tokenId], "Token does not exist");
        return _tokenURIs[tokenId];
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title ERC1155Basic
 * @dev Multi-token standard for games and collections
 */
contract ERC1155Basic is ERC1155, Ownable {
    using Strings for uint256;

    string public name;
    string public symbol;
    uint256 public nextTokenId;

    mapping(uint256 => string) private _tokenURIs;
    mapping(uint256 => uint256) public tokenSupply;
    mapping(uint256 => uint256) public maxTokenSupply;

    event TokenCreated(uint256 indexed tokenId, uint256 maxSupply);
    event TokenMinted(address indexed to, uint256 indexed tokenId, uint256 amount);

    constructor(
        string memory _name,
        string memory _symbol,
        string memory uri
    ) ERC1155(uri) Ownable(msg.sender) {
        name = _name;
        symbol = _symbol;
    }

    function createToken(uint256 maxSupply, string memory tokenURI) external onlyOwner returns (uint256) {
        uint256 tokenId = nextTokenId++;
        maxTokenSupply[tokenId] = maxSupply;
        _tokenURIs[tokenId] = tokenURI;
        emit TokenCreated(tokenId, maxSupply);
        return tokenId;
    }

    function mint(
        address to,
        uint256 tokenId,
        uint256 amount
    ) external onlyOwner {
        require(tokenId < nextTokenId, "Token does not exist");
        require(
            tokenSupply[tokenId] + amount <= maxTokenSupply[tokenId],
            "Max supply exceeded"
        );

        tokenSupply[tokenId] += amount;
        _mint(to, tokenId, amount, "");
        emit TokenMinted(to, tokenId, amount);
    }

    function batchMint(
        address to,
        uint256[] memory tokenIds,
        uint256[] memory amounts
    ) external onlyOwner {
        require(tokenIds.length == amounts.length, "Length mismatch");

        for (uint256 i = 0; i < tokenIds.length; i++) {
            require(tokenIds[i] < nextTokenId, "Token does not exist");
            require(
                tokenSupply[tokenIds[i]] + amounts[i] <= maxTokenSupply[tokenIds[i]],
                "Max supply exceeded"
            );
            tokenSupply[tokenIds[i]] += amounts[i];
        }

        _mintBatch(to, tokenIds, amounts, "");
    }

    function uri(uint256 tokenId) public view override returns (string memory) {
        require(tokenId < nextTokenId, "Token does not exist");
        return _tokenURIs[tokenId];
    }

    function setURI(uint256 tokenId, string memory tokenURI) external onlyOwner {
        require(tokenId < nextTokenId, "Token does not exist");
        _tokenURIs[tokenId] = tokenURI;
    }
}

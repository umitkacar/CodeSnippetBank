// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ERC721URIStorageNFT
 * @dev NFT with individual token URI storage
 */
contract ERC721URIStorageNFT is ERC721, ERC721URIStorage, Ownable {
    uint256 public nextTokenId;

    event TokenMinted(address indexed to, uint256 indexed tokenId, string uri);

    constructor(
        string memory name,
        string memory symbol
    ) ERC721(name, symbol) Ownable(msg.sender) {}

    function mint(address to, string memory uri) external onlyOwner returns (uint256) {
        uint256 tokenId = nextTokenId++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        emit TokenMinted(to, tokenId, uri);
        return tokenId;
    }

    function batchMintWithURI(
        address[] calldata recipients,
        string[] calldata uris
    ) external onlyOwner {
        require(recipients.length == uris.length, "Length mismatch");

        for (uint256 i = 0; i < recipients.length; i++) {
            uint256 tokenId = nextTokenId++;
            _safeMint(recipients[i], tokenId);
            _setTokenURI(tokenId, uris[i]);
            emit TokenMinted(recipients[i], tokenId, uris[i]);
        }
    }

    function updateTokenURI(uint256 tokenId, string memory uri) external onlyOwner {
        require(ownerOf(tokenId) != address(0), "Token does not exist");
        _setTokenURI(tokenId, uri);
    }

    // Required overrides
    function tokenURI(
        uint256 tokenId
    ) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(
        bytes4 interfaceId
    ) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}

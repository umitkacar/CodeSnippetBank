// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ERC721Royalty
 * @dev NFT with EIP-2981 royalty standard
 */
contract ERC721Royalty is ERC721, ERC2981, Ownable {
    uint256 public nextTokenId;
    uint256 public maxSupply;
    string private _baseTokenURI;

    uint96 public defaultRoyaltyFee = 500; // 5%

    event RoyaltyUpdated(uint256 indexed tokenId, address receiver, uint96 feeNumerator);

    constructor(
        string memory name,
        string memory symbol,
        uint256 _maxSupply,
        string memory baseURI
    ) ERC721(name, symbol) Ownable(msg.sender) {
        maxSupply = _maxSupply;
        _baseTokenURI = baseURI;
        _setDefaultRoyalty(msg.sender, defaultRoyaltyFee);
    }

    function mint(address to) external onlyOwner {
        require(nextTokenId < maxSupply, "Max supply reached");
        _safeMint(to, nextTokenId++);
    }

    function setDefaultRoyalty(address receiver, uint96 feeNumerator) external onlyOwner {
        _setDefaultRoyalty(receiver, feeNumerator);
        defaultRoyaltyFee = feeNumerator;
    }

    function setTokenRoyalty(
        uint256 tokenId,
        address receiver,
        uint96 feeNumerator
    ) external onlyOwner {
        _setTokenRoyalty(tokenId, receiver, feeNumerator);
        emit RoyaltyUpdated(tokenId, receiver, feeNumerator);
    }

    function deleteDefaultRoyalty() external onlyOwner {
        _deleteDefaultRoyalty();
    }

    function resetTokenRoyalty(uint256 tokenId) external onlyOwner {
        _resetTokenRoyalty(tokenId);
    }

    function _baseURI() internal view override returns (string memory) {
        return _baseTokenURI;
    }

    function supportsInterface(
        bytes4 interfaceId
    ) public view override(ERC721, ERC2981) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}

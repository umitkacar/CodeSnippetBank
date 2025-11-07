// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ERC721Merkle
 * @dev NFT with Merkle tree whitelist for gas-efficient whitelisting
 */
contract ERC721Merkle is ERC721, Ownable {
    uint256 public nextTokenId;
    uint256 public maxSupply;
    bytes32 public merkleRoot;

    mapping(address => bool) public hasMinted;

    uint256 public whitelistPrice;
    uint256 public publicPrice;
    bool public whitelistActive = true;
    bool public publicSaleActive = false;

    event MerkleRootUpdated(bytes32 newRoot);
    event WhitelistMint(address indexed minter, uint256 tokenId);
    event PublicMint(address indexed minter, uint256 tokenId);

    constructor(
        string memory name,
        string memory symbol,
        uint256 _maxSupply,
        bytes32 _merkleRoot,
        uint256 _whitelistPrice,
        uint256 _publicPrice
    ) ERC721(name, symbol) Ownable(msg.sender) {
        maxSupply = _maxSupply;
        merkleRoot = _merkleRoot;
        whitelistPrice = _whitelistPrice;
        publicPrice = _publicPrice;
    }

    function whitelistMint(bytes32[] calldata proof) external payable {
        require(whitelistActive, "Whitelist not active");
        require(!hasMinted[msg.sender], "Already minted");
        require(nextTokenId < maxSupply, "Max supply reached");
        require(msg.value >= whitelistPrice, "Insufficient payment");

        bytes32 leaf = keccak256(abi.encodePacked(msg.sender));
        require(MerkleProof.verify(proof, merkleRoot, leaf), "Invalid proof");

        hasMinted[msg.sender] = true;
        uint256 tokenId = nextTokenId++;
        _safeMint(msg.sender, tokenId);

        emit WhitelistMint(msg.sender, tokenId);
    }

    function publicMint() external payable {
        require(publicSaleActive, "Public sale not active");
        require(nextTokenId < maxSupply, "Max supply reached");
        require(msg.value >= publicPrice, "Insufficient payment");

        uint256 tokenId = nextTokenId++;
        _safeMint(msg.sender, tokenId);

        emit PublicMint(msg.sender, tokenId);
    }

    function setMerkleRoot(bytes32 _merkleRoot) external onlyOwner {
        merkleRoot = _merkleRoot;
        emit MerkleRootUpdated(_merkleRoot);
    }

    function setWhitelistActive(bool active) external onlyOwner {
        whitelistActive = active;
    }

    function setPublicSaleActive(bool active) external onlyOwner {
        publicSaleActive = active;
    }

    function setPrices(uint256 _whitelistPrice, uint256 _publicPrice) external onlyOwner {
        whitelistPrice = _whitelistPrice;
        publicPrice = _publicPrice;
    }

    function withdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}

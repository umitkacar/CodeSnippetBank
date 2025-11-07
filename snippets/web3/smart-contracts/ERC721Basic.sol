// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title ERC721Basic
 * @dev Production-ready NFT collection with minting controls
 */
contract ERC721Basic is ERC721, ERC721Burnable, Ownable {
    using Strings for uint256;

    uint256 public maxSupply;
    uint256 public currentTokenId;
    uint256 public mintPrice;
    string private baseTokenURI;

    mapping(address => uint256) public mintedPerAddress;
    uint256 public maxMintPerAddress = 5;

    event NFTMinted(address indexed to, uint256 indexed tokenId);
    event BaseURIUpdated(string newBaseURI);
    event MintPriceUpdated(uint256 newPrice);

    constructor(
        string memory name,
        string memory symbol,
        uint256 _maxSupply,
        uint256 _mintPrice,
        string memory _baseTokenURI
    ) ERC721(name, symbol) Ownable(msg.sender) {
        maxSupply = _maxSupply;
        mintPrice = _mintPrice;
        baseTokenURI = _baseTokenURI;
    }

    function mint(uint256 quantity) external payable {
        require(currentTokenId + quantity <= maxSupply, "Max supply reached");
        require(msg.value >= mintPrice * quantity, "Insufficient payment");
        require(
            mintedPerAddress[msg.sender] + quantity <= maxMintPerAddress,
            "Max mint per address exceeded"
        );

        for (uint256 i = 0; i < quantity; i++) {
            uint256 newTokenId = ++currentTokenId;
            _safeMint(msg.sender, newTokenId);
            emit NFTMinted(msg.sender, newTokenId);
        }

        mintedPerAddress[msg.sender] += quantity;
    }

    function ownerMint(address to, uint256 quantity) external onlyOwner {
        require(currentTokenId + quantity <= maxSupply, "Max supply reached");

        for (uint256 i = 0; i < quantity; i++) {
            uint256 newTokenId = ++currentTokenId;
            _safeMint(to, newTokenId);
            emit NFTMinted(to, newTokenId);
        }
    }

    function setBaseURI(string memory _baseTokenURI) external onlyOwner {
        baseTokenURI = _baseTokenURI;
        emit BaseURIUpdated(_baseTokenURI);
    }

    function setMintPrice(uint256 _mintPrice) external onlyOwner {
        mintPrice = _mintPrice;
        emit MintPriceUpdated(_mintPrice);
    }

    function setMaxMintPerAddress(uint256 _max) external onlyOwner {
        maxMintPerAddress = _max;
    }

    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        payable(owner()).transfer(balance);
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(ownerOf(tokenId) != address(0), "Token does not exist");
        return string(abi.encodePacked(baseTokenURI, tokenId.toString(), ".json"));
    }

    function _baseURI() internal view override returns (string memory) {
        return baseTokenURI;
    }
}

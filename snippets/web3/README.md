# 🔗 Web3 & Blockchain Snippets

<div align="center">

![Ethereum](https://img.shields.io/badge/Ethereum-3C3C3D?style=for-the-badge&logo=ethereum&logoColor=white)
![Solidity](https://img.shields.io/badge/Solidity-363636?style=for-the-badge&logo=solidity&logoColor=white)
![Web3.js](https://img.shields.io/badge/Web3.js-F16822?style=for-the-badge&logo=web3.js&logoColor=white)
![IPFS](https://img.shields.io/badge/IPFS-65C2CB?style=for-the-badge&logo=ipfs&logoColor=white)

</div>

## ⛓️ Smart Contracts

### ERC-20 Token (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract ModernToken is ERC20, Ownable, Pausable {
    uint256 public constant MAX_SUPPLY = 1000000 * 10**18; // 1 million tokens
    mapping(address => bool) public blacklisted;

    event Blacklisted(address indexed account);
    event Whitelisted(address indexed account);

    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply
    ) ERC20(name, symbol) {
        require(initialSupply <= MAX_SUPPLY, "Exceeds max supply");
        _mint(msg.sender, initialSupply);
    }

    function mint(address to, uint256 amount) public onlyOwner {
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");
        _mint(to, amount);
    }

    function burn(uint256 amount) public {
        _burn(msg.sender, amount);
    }

    function pause() public onlyOwner {
        _pause();
    }

    function unpause() public onlyOwner {
        _unpause();
    }

    function blacklist(address account) public onlyOwner {
        blacklisted[account] = true;
        emit Blacklisted(account);
    }

    function whitelist(address account) public onlyOwner {
        blacklisted[account] = false;
        emit Whitelisted(account);
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        require(!blacklisted[from], "Sender is blacklisted");
        require(!blacklisted[to], "Recipient is blacklisted");
        super._beforeTokenTransfer(from, to, amount);
    }
}
```

### NFT Collection with Royalties

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract ModernNFT is ERC721URIStorage, ERC2981, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    uint256 public constant MAX_SUPPLY = 10000;
    uint256 public constant MINT_PRICE = 0.05 ether;
    uint256 public constant MAX_PER_WALLET = 5;

    mapping(address => uint256) public mintCount;
    string public baseTokenURI;

    event NFTMinted(address indexed to, uint256 tokenId);

    constructor(
        string memory name,
        string memory symbol,
        string memory _baseTokenURI,
        address royaltyReceiver,
        uint96 royaltyFeeNumerator
    ) ERC721(name, symbol) {
        baseTokenURI = _baseTokenURI;
        _setDefaultRoyalty(royaltyReceiver, royaltyFeeNumerator); // e.g., 500 = 5%
    }

    function mint(uint256 quantity) public payable {
        require(quantity > 0, "Quantity must be positive");
        require(_tokenIds.current() + quantity <= MAX_SUPPLY, "Max supply reached");
        require(mintCount[msg.sender] + quantity <= MAX_PER_WALLET, "Max per wallet exceeded");
        require(msg.value >= MINT_PRICE * quantity, "Insufficient payment");

        for (uint256 i = 0; i < quantity; i++) {
            _tokenIds.increment();
            uint256 newTokenId = _tokenIds.current();

            _safeMint(msg.sender, newTokenId);
            _setTokenURI(newTokenId, string(abi.encodePacked(baseTokenURI, Strings.toString(newTokenId), ".json")));

            mintCount[msg.sender]++;
            emit NFTMinted(msg.sender, newTokenId);
        }
    }

    function withdraw() public onlyOwner {
        uint256 balance = address(this).balance;
        payable(owner()).transfer(balance);
    }

    function setBaseURI(string memory _baseTokenURI) public onlyOwner {
        baseTokenURI = _baseTokenURI;
    }

    function setRoyaltyInfo(address receiver, uint96 feeNumerator) public onlyOwner {
        _setDefaultRoyalty(receiver, feeNumerator);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721URIStorage, ERC2981)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
```

## 🌐 Web3 Integration

### ethers.js v6 (Latest)

```typescript
// lib/web3.ts
import { ethers } from 'ethers'

export class Web3Provider {
  private provider: ethers.BrowserProvider | null = null
  private signer: ethers.JsonRpcSigner | null = null

  async connect() {
    if (!window.ethereum) {
      throw new Error('No wallet detected')
    }

    this.provider = new ethers.BrowserProvider(window.ethereum)

    // Request account access
    await this.provider.send('eth_requestAccounts', [])

    this.signer = await this.provider.getSigner()

    return {
      address: await this.signer.getAddress(),
      chainId: (await this.provider.getNetwork()).chainId,
    }
  }

  async getBalance(address: string) {
    if (!this.provider) throw new Error('Not connected')

    const balance = await this.provider.getBalance(address)
    return ethers.formatEther(balance)
  }

  async sendTransaction(to: string, amount: string) {
    if (!this.signer) throw new Error('Not connected')

    const tx = await this.signer.sendTransaction({
      to,
      value: ethers.parseEther(amount),
    })

    const receipt = await tx.wait()
    return receipt
  }

  async signMessage(message: string) {
    if (!this.signer) throw new Error('Not connected')
    return await this.signer.signMessage(message)
  }
}

// Contract interaction
export class ContractHandler {
  private contract: ethers.Contract

  constructor(
    address: string,
    abi: any[],
    signerOrProvider: ethers.Signer | ethers.Provider
  ) {
    this.contract = new ethers.Contract(address, abi, signerOrProvider)
  }

  // Read function
  async read(functionName: string, ...args: any[]) {
    return await this.contract[functionName](...args)
  }

  // Write function
  async write(functionName: string, ...args: any[]) {
    const tx = await this.contract[functionName](...args)
    return await tx.wait()
  }

  // Listen to events
  onEvent(eventName: string, callback: (...args: any[]) => void) {
    this.contract.on(eventName, callback)
  }
}

// Usage example
const web3 = new Web3Provider()
await web3.connect()

const nftContract = new ContractHandler(
  '0x...',
  NFT_ABI,
  await web3.getSigner()
)

// Mint NFT
const receipt = await nftContract.write('mint', 1, {
  value: ethers.parseEther('0.05'),
})

// Listen to mint events
nftContract.onEvent('NFTMinted', (to, tokenId) => {
  console.log(`Minted token ${tokenId} to ${to}`)
})
```

### wagmi + viem (Modern React Hooks)

```typescript
// app/providers.tsx
'use client'

import { WagmiProvider, createConfig, http } from 'wagmi'
import { mainnet, polygon, optimism } from 'wagmi/chains'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConnectKitProvider, getDefaultConfig } from 'connectkit'

const config = createConfig(
  getDefaultConfig({
    appName: 'My Modern dApp',
    walletConnectProjectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID!,
    chains: [mainnet, polygon, optimism],
    transports: {
      [mainnet.id]: http(),
      [polygon.id]: http(),
      [optimism.id]: http(),
    },
  })
)

const queryClient = new QueryClient()

export function Web3Providers({ children }: { children: React.ReactNode }) {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <ConnectKitProvider>{children}</ConnectKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  )
}

// components/MintNFT.tsx
'use client'

import { useAccount, useWriteContract, useWaitForTransactionReceipt } from 'wagmi'
import { parseEther } from 'viem'
import { NFT_ABI, NFT_ADDRESS } from '@/lib/contracts'

export function MintNFT() {
  const { address, isConnected } = useAccount()
  const { writeContract, data: hash } = useWriteContract()

  const { isLoading, isSuccess } = useWaitForTransactionReceipt({
    hash,
  })

  const handleMint = async () => {
    writeContract({
      address: NFT_ADDRESS,
      abi: NFT_ABI,
      functionName: 'mint',
      args: [1],
      value: parseEther('0.05'),
    })
  }

  if (!isConnected) return <div>Please connect your wallet</div>

  return (
    <div>
      <button
        onClick={handleMint}
        disabled={isLoading}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        {isLoading ? 'Minting...' : 'Mint NFT'}
      </button>

      {isSuccess && <div>NFT Minted Successfully!</div>}
    </div>
  )
}
```

### IPFS Integration

```typescript
// lib/ipfs.ts
import { create } from 'ipfs-http-client'
import { NFTStorage, File } from 'nft.storage'

// Using IPFS HTTP Client
export class IPFSUploader {
  private client: any

  constructor() {
    this.client = create({
      host: 'ipfs.infura.io',
      port: 5001,
      protocol: 'https',
      headers: {
        authorization: `Basic ${Buffer.from(
          `${process.env.INFURA_PROJECT_ID}:${process.env.INFURA_SECRET}`
        ).toString('base64')}`,
      },
    })
  }

  async uploadFile(file: File) {
    const added = await this.client.add(file)
    return `ipfs://${added.path}`
  }

  async uploadJSON(data: any) {
    const json = JSON.stringify(data)
    const added = await this.client.add(json)
    return `ipfs://${added.path}`
  }
}

// Using NFT.Storage (Recommended for NFTs)
export class NFTStorageUploader {
  private client: NFTStorage

  constructor() {
    this.client = new NFTStorage({
      token: process.env.NFT_STORAGE_KEY!,
    })
  }

  async uploadNFT(
    imageFile: File,
    metadata: {
      name: string
      description: string
      attributes?: Array<{ trait_type: string; value: string | number }>
    }
  ) {
    const nft = await this.client.store({
      image: imageFile,
      name: metadata.name,
      description: metadata.description,
      attributes: metadata.attributes || [],
    })

    return {
      url: nft.url,
      ipnft: nft.ipnft,
      data: nft.data,
    }
  }
}

// Usage
const uploader = new NFTStorageUploader()
const result = await uploader.uploadNFT(imageFile, {
  name: 'Cool NFT #1',
  description: 'An awesome NFT',
  attributes: [
    { trait_type: 'Background', value: 'Blue' },
    { trait_type: 'Rarity', value: 'Legendary' },
  ],
})

console.log(`NFT metadata: ${result.url}`)
```

## 📚 Popular Repositories

- **[Hardhat](https://github.com/NomicFoundation/hardhat)** ⭐ 7k+ - Ethereum development environment
- **[wagmi](https://github.com/wevm/wagmi)** ⭐ 5k+ - React Hooks for Ethereum
- **[viem](https://github.com/wevm/viem)** ⭐ 2k+ - TypeScript interface for Ethereum
- **[OpenZeppelin Contracts](https://github.com/OpenZeppelin/openzeppelin-contracts)** ⭐ 24k+ - Secure smart contracts
- **[ethers.js](https://github.com/ethers-io/ethers.js)** ⭐ 7.5k+ - Ethereum library

---

<div align="center">

**[⬅️ Back: Backend](../backend/README.md)** | **[Next: DevOps →](../devops/README.md)**

</div>

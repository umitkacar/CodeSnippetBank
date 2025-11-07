/**
 * IPFS Upload Utilities
 * Upload files and metadata to IPFS
 */

// Using Pinata SDK as an example
export interface IPFSUploadResult {
  IpfsHash: string;
  PinSize: number;
  Timestamp: string;
  url: string;
}

// Upload file to IPFS via Pinata
export async function uploadFileToPinata(
  file: File,
  apiKey: string,
  apiSecret: string
): Promise<IPFSUploadResult> {
  const formData = new FormData();
  formData.append('file', file);

  const metadata = JSON.stringify({
    name: file.name,
  });
  formData.append('pinataMetadata', metadata);

  const options = JSON.stringify({
    cidVersion: 1,
  });
  formData.append('pinataOptions', options);

  const response = await fetch('https://api.pinata.cloud/pinning/pinFileToIPFS', {
    method: 'POST',
    headers: {
      pinata_api_key: apiKey,
      pinata_secret_api_key: apiSecret,
    },
    body: formData,
  });

  const result = await response.json();

  return {
    ...result,
    url: `https://ipfs.io/ipfs/${result.IpfsHash}`,
  };
}

// Upload JSON metadata to IPFS
export async function uploadJSONToPinata(
  metadata: any,
  apiKey: string,
  apiSecret: string
): Promise<IPFSUploadResult> {
  const response = await fetch('https://api.pinata.cloud/pinning/pinJSONToIPFS', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      pinata_api_key: apiKey,
      pinata_secret_api_key: apiSecret,
    },
    body: JSON.stringify({
      pinataContent: metadata,
      pinataMetadata: {
        name: metadata.name || 'metadata.json',
      },
    }),
  });

  const result = await response.json();

  return {
    ...result,
    url: `https://ipfs.io/ipfs/${result.IpfsHash}`,
  };
}

// Upload with NFT.Storage
export async function uploadToNFTStorage(
  file: File,
  apiKey: string
): Promise<{ url: string; cid: string }> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('https://api.nft.storage/upload', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
    },
    body: formData,
  });

  const result = await response.json();

  return {
    cid: result.value.cid,
    url: `https://ipfs.io/ipfs/${result.value.cid}`,
  };
}

// Create NFT metadata
export interface NFTMetadataInput {
  name: string;
  description: string;
  image: string; // IPFS URI
  attributes?: Array<{ trait_type: string; value: string | number }>;
  external_url?: string;
  animation_url?: string;
}

export function createNFTMetadata(input: NFTMetadataInput) {
  return {
    name: input.name,
    description: input.description,
    image: input.image,
    attributes: input.attributes || [],
    external_url: input.external_url,
    animation_url: input.animation_url,
  };
}

// Upload image and metadata for NFT
export async function uploadNFT(
  imageFile: File,
  metadata: Omit<NFTMetadataInput, 'image'>,
  apiKey: string,
  apiSecret: string
): Promise<{ imageUrl: string; metadataUrl: string }> {
  // Upload image first
  const imageResult = await uploadFileToPinata(imageFile, apiKey, apiSecret);

  // Create metadata with image IPFS hash
  const fullMetadata = createNFTMetadata({
    ...metadata,
    image: `ipfs://${imageResult.IpfsHash}`,
  });

  // Upload metadata
  const metadataResult = await uploadJSONToPinata(fullMetadata, apiKey, apiSecret);

  return {
    imageUrl: imageResult.url,
    metadataUrl: `ipfs://${metadataResult.IpfsHash}`,
  };
}

// Batch upload NFT collection
export async function uploadNFTCollection(
  files: File[],
  metadataList: Array<Omit<NFTMetadataInput, 'image'>>,
  apiKey: string,
  apiSecret: string
): Promise<Array<{ imageUrl: string; metadataUrl: string }>> {
  if (files.length !== metadataList.length) {
    throw new Error('Files and metadata count mismatch');
  }

  const results = await Promise.all(
    files.map((file, index) =>
      uploadNFT(file, metadataList[index], apiKey, apiSecret)
    )
  );

  return results;
}

// Convert IPFS URI to HTTP URL
export function ipfsToHttp(ipfsUri: string, gateway = 'https://ipfs.io'): string {
  if (!ipfsUri.startsWith('ipfs://')) {
    return ipfsUri;
  }

  const hash = ipfsUri.replace('ipfs://', '');
  return `${gateway}/ipfs/${hash}`;
}

// React hook for IPFS upload
export function useIPFSUpload(apiKey: string, apiSecret: string) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    setError(null);

    try {
      const result = await uploadFileToPinata(file, apiKey, apiSecret);
      return result;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  const uploadMetadata = async (metadata: any) => {
    setIsUploading(true);
    setError(null);

    try {
      const result = await uploadJSONToPinata(metadata, apiKey, apiSecret);
      return result;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  const uploadNFTData = async (
    imageFile: File,
    metadata: Omit<NFTMetadataInput, 'image'>
  ) => {
    setIsUploading(true);
    setError(null);

    try {
      const result = await uploadNFT(imageFile, metadata, apiKey, apiSecret);
      return result;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  return {
    uploadFile,
    uploadMetadata,
    uploadNFTData,
    isUploading,
    error,
  };
}

export default {
  uploadFileToPinata,
  uploadJSONToPinata,
  uploadToNFTStorage,
  createNFTMetadata,
  uploadNFT,
  uploadNFTCollection,
  ipfsToHttp,
  useIPFSUpload,
};

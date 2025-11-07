/**
 * Contract Verification Utils
 * Verify contract code on block explorers
 */

import axios from 'axios';

export interface VerificationParams {
  contractAddress: string;
  sourceCode: string;
  contractName: string;
  compilerVersion: string;
  optimizationUsed: boolean;
  runs: number;
  constructorArguments?: string;
  evmVersion?: string;
  licenseType?: number;
}

// Etherscan verification
export async function verifyOnEtherscan(
  params: VerificationParams,
  apiKey: string,
  chainId: number = 1
): Promise<{ guid: string }> {
  const baseUrls: Record<number, string> = {
    1: 'https://api.etherscan.io',
    5: 'https://api-goerli.etherscan.io',
    137: 'https://api.polygonscan.com',
    42161: 'https://api.arbiscan.io',
    10: 'https://api-optimistic.etherscan.io',
  };

  const baseUrl = baseUrls[chainId] || baseUrls[1];

  const response = await axios.post(`${baseUrl}/api`, {
    apikey: apiKey,
    module: 'contract',
    action: 'verifysourcecode',
    contractaddress: params.contractAddress,
    sourceCode: params.sourceCode,
    codeformat: 'solidity-single-file',
    contractname: params.contractName,
    compilerversion: params.compilerVersion,
    optimizationUsed: params.optimizationUsed ? 1 : 0,
    runs: params.runs,
    constructorArguements: params.constructorArguments || '',
    evmversion: params.evmVersion || 'default',
    licenseType: params.licenseType || 1,
  });

  if (response.data.status !== '1') {
    throw new Error(response.data.result);
  }

  return { guid: response.data.result };
}

// Check verification status
export async function checkVerificationStatus(
  guid: string,
  apiKey: string,
  chainId: number = 1
): Promise<{ status: string; result: string }> {
  const baseUrls: Record<number, string> = {
    1: 'https://api.etherscan.io',
    5: 'https://api-goerli.etherscan.io',
    137: 'https://api.polygonscan.com',
    42161: 'https://api.arbiscan.io',
    10: 'https://api-optimistic.etherscan.io',
  };

  const baseUrl = baseUrls[chainId] || baseUrls[1];

  const response = await axios.get(`${baseUrl}/api`, {
    params: {
      apikey: apiKey,
      module: 'contract',
      action: 'checkverifystatus',
      guid,
    },
  });

  return {
    status: response.data.status,
    result: response.data.result,
  };
}

// Get verified contract source
export async function getContractSource(
  contractAddress: string,
  apiKey: string,
  chainId: number = 1
): Promise<any> {
  const baseUrls: Record<number, string> = {
    1: 'https://api.etherscan.io',
    5: 'https://api-goerli.etherscan.io',
    137: 'https://api.polygonscan.com',
    42161: 'https://api.arbiscan.io',
    10: 'https://api-optimistic.etherscan.io',
  };

  const baseUrl = baseUrls[chainId] || baseUrls[1];

  const response = await axios.get(`${baseUrl}/api`, {
    params: {
      apikey: apiKey,
      module: 'contract',
      action: 'getsourcecode',
      address: contractAddress,
    },
  });

  return response.data.result[0];
}

export default {
  verifyOnEtherscan,
  checkVerificationStatus,
  getContractSource,
};

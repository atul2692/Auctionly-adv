// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title PriceConverter
 * @dev Library for converting between USD and ETH
 * In a production environment, this would use Chainlink or another oracle
 * For this demo, we'll use a simplified fixed rate converter
 */
library PriceConverter {
    // For demo purposes, we'll set a fixed ETH/USD price
    // In production, you'd use a Chainlink price feed
    uint256 private constant ETH_USD_PRICE = 3000 * 1e18; // 1 ETH = $3000 (with 18 decimals)
    
    /**
     * @dev Convert USD amount to ETH (wei)
     * @param usdAmount Amount in USD (with 18 decimals)
     * @return ethAmount Amount in ETH (wei)
     */
    function usdToEth(uint256 usdAmount) internal pure returns (uint256 ethAmount) {
        // Convert USD to ETH: usdAmount / ETH_USD_PRICE
        ethAmount = (usdAmount * 1e18) / ETH_USD_PRICE;
        return ethAmount;
    }
    
    /**
     * @dev Convert ETH (wei) amount to USD
     * @param ethAmount Amount in ETH (wei)
     * @return usdAmount Amount in USD (with 18 decimals)
     */
    function ethToUsd(uint256 ethAmount) internal pure returns (uint256 usdAmount) {
        // Convert ETH to USD: ethAmount * ETH_USD_PRICE
        usdAmount = (ethAmount * ETH_USD_PRICE) / 1e18;
        return usdAmount;
    }
} 
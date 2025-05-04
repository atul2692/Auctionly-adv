// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./PriceConverter.sol";
import "./AuctionContract.sol";

/**
 * @title PaymentProcessor
 * @dev Contract for processing payments with USD to ETH conversion
 */
contract PaymentProcessor {
    using PriceConverter for uint256;
    
    AuctionContract private _auctionContract;
    
    event PaymentProcessed(uint256 indexed auctionId, address buyer, uint256 usdAmount, uint256 ethAmount);
    
    /**
     * @dev Constructor sets the auction contract address
     * @param auctionContractAddress Address of the deployed AuctionContract
     */
    constructor(address auctionContractAddress) {
        _auctionContract = AuctionContract(auctionContractAddress);
    }
    
    /**
     * @dev Process payment for an auction in ETH based on USD amount
     * @param auctionId ID of the auction to pay for
     * @param usdAmount Amount in USD (with 18 decimals)
     */
    function processPayment(uint256 auctionId, uint256 usdAmount) external payable {
        // Calculate the equivalent ETH amount
        uint256 ethAmount = usdAmount.usdToEth();
        
        // Verify that enough ETH was sent
        require(msg.value >= ethAmount, "Insufficient ETH sent for payment");
        
        // Call the auction contract's makePayment function
        _auctionContract.makePayment{value: ethAmount}(auctionId);
        
        // Refund excess ETH if any
        if (msg.value > ethAmount) {
            (bool success, ) = payable(msg.sender).call{value: msg.value - ethAmount}("");
            require(success, "Failed to refund excess ETH");
        }
        
        emit PaymentProcessed(auctionId, msg.sender, usdAmount, ethAmount);
    }
    
    /**
     * @dev Calculate the ETH amount required for a USD payment
     * @param usdAmount Amount in USD (with 18 decimals)
     * @return ethAmount Amount in ETH (wei)
     */
    function getEthAmount(uint256 usdAmount) external pure returns (uint256) {
        return usdAmount.usdToEth();
    }
    
    /**
     * @dev Allow the contract to receive ETH
     */
    receive() external payable {}
    
    /**
     * @dev Fallback function
     */
    fallback() external payable {}
} 
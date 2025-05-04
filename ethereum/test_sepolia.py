#!/usr/bin/env python
"""
Simple test script to verify Ethereum connection to Sepolia testnet.
"""

import os
import sys
import logging
from web3 import Web3

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sepolia testnet via Infura
INFURA_API_KEY = "c592d537c4514e66b9af8b15770bc347"  # Your Infura API key from settings
ETH_NETWORK_URL = f"https://sepolia.infura.io/v3/{INFURA_API_KEY}"
AUCTION_CONTRACT_ADDRESS = "0x6eF09D25cD8AAb5A835FF721a250D549DF94313c"  # Your deployed contract address

def test_connection():
    """Test connection to Sepolia testnet"""
    try:
        # Create Web3 instance
        logger.info(f"Connecting to Ethereum node at {ETH_NETWORK_URL}...")
        w3 = Web3(Web3.HTTPProvider(ETH_NETWORK_URL))
        
        # Check connection
        if w3.is_connected():
            logger.info("✅ Successfully connected to Ethereum node!")
            chain_id = w3.eth.chain_id
            logger.info(f"Chain ID: {chain_id} (Should be 11155111 for Sepolia)")
            
            # Get the latest block number
            latest_block = w3.eth.block_number
            logger.info(f"Latest block number: {latest_block}")
            
            # Create a minimal ABI just to test contract connection
            minimal_abi = [
                {
                    "inputs": [{"internalType": "uint256", "name": "_auctionId", "type": "uint256"}],
                    "name": "getAuction",
                    "outputs": [
                        {"internalType": "address", "name": "seller", "type": "address"},
                        {"internalType": "uint256", "name": "startingPrice", "type": "uint256"},
                        {"internalType": "uint256", "name": "currentPrice", "type": "uint256"},
                        {"internalType": "address", "name": "highestBidder", "type": "address"},
                        {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                        {"internalType": "bool", "name": "ended", "type": "bool"},
                        {"internalType": "bool", "name": "paid", "type": "bool"}
                    ],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
            
            # Try to create contract instance
            try:
                contract = w3.eth.contract(
                    address=w3.to_checksum_address(AUCTION_CONTRACT_ADDRESS),
                    abi=minimal_abi
                )
                logger.info(f"✅ Successfully created contract instance for: {AUCTION_CONTRACT_ADDRESS}")
                
                # Try to call a contract function
                try:
                    # Try to get auction with ID 0 (if it exists)
                    result = contract.functions.getAuction(0).call()
                    logger.info(f"Successfully called getAuction(0): {result}")
                except Exception as call_error:
                    logger.warning(f"Could not call contract function: {call_error}")
                    logger.info("This could be normal if auction ID 0 doesn't exist")
                
            except Exception as contract_error:
                logger.error(f"❌ Could not create contract instance: {contract_error}")
            
        else:
            logger.error("❌ Failed to connect to Ethereum node")
            logger.error(f"Provider URL: {ETH_NETWORK_URL}")
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection() 
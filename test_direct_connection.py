#!/usr/bin/env python
"""
Direct test script to verify Ethereum connection is working without Django settings.
"""

import sys
import logging
import os
from web3 import Web3
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Hardcoded settings for testing
INFURA_API_KEY = "c592d537c4514e66b9af8b15770bc347"  # Already in settings.py
ETH_NETWORK_URL = f"https://sepolia.infura.io/v3/{INFURA_API_KEY}"
AUCTION_CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"  # Placeholder address

try:
    # Connect to Ethereum node
    logger.info(f"Connecting to Ethereum node at {ETH_NETWORK_URL}...")
    w3 = Web3(Web3.HTTPProvider(ETH_NETWORK_URL))
    
    # Check connection
    if w3.is_connected():
        logger.info("✅ Successfully connected to Ethereum node!")
        
        # Get the latest block number
        latest_block = w3.eth.block_number
        if latest_block:
            logger.info(f"Latest block number: {latest_block}")
        
        # Create a minimal ABI just for testing connection
        minimal_abi = [
            {
                "type": "function",
                "name": "balanceOf",
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "outputs": [{"name": "balance", "type": "uint256"}],
                "payable": False,
                "stateMutability": "view"
            }
        ]
        
        # Try to create contract instance
        try:
            contract = w3.eth.contract(
                address=w3.to_checksum_address(AUCTION_CONTRACT_ADDRESS), 
                abi=minimal_abi
            )
            logger.info(f"✅ Successfully created contract instance for: {AUCTION_CONTRACT_ADDRESS}")
            logger.info("Note: This is just testing the connection, not the actual contract functionality")
        except Exception as contract_error:
            logger.warning(f"Could not create contract instance: {contract_error}")
            logger.info("This is expected if the contract address is a placeholder or incorrect")
        
    else:
        logger.error("❌ Failed to connect to Ethereum node")
        logger.error(f"Provider URL: {ETH_NETWORK_URL}")
    
except Exception as e:
    logger.error(f"❌ Error: {str(e)}")
    
print("\nFollow the instructions in ethereum/README_ETHEREUM_SETUP.md to resolve any issues.") 
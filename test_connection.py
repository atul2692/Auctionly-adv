#!/usr/bin/env python
"""
Test script to verify Ethereum connection is working.
"""

import sys
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the event listener
    from ethereum.event_listener import EventListener
    
    # Create a listener instance
    logger.info("Creating EventListener instance...")
    listener = EventListener()
    
    # Check connection
    if listener.w3 and listener.w3.is_connected():
        logger.info("✅ Successfully connected to Ethereum node!")
        logger.info(f"Provider URL: {listener.web3_provider}")
        
        # Get the latest block number
        latest_block = listener.get_latest_block()
        if latest_block:
            logger.info(f"Latest block number: {latest_block}")
        
        # Test contract connection
        if listener.contract:
            logger.info(f"✅ Successfully connected to contract: {listener.contract_address}")
        else:
            logger.error("❌ Failed to connect to contract")
        
    else:
        logger.error("❌ Failed to connect to Ethereum node")
        logger.error(f"Provider URL: {listener.web3_provider}")
    
except Exception as e:
    logger.error(f"❌ Error: {str(e)}")
    
print("\nFollow the instructions in ethereum/README_ETHEREUM_SETUP.md to resolve any issues.") 
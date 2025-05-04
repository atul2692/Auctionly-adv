#!/usr/bin/env python
"""
Test script for Ethereum event listener without Django dependencies.
"""

import sys
import logging
import os
import time
from web3 import Web3
from datetime import datetime, timezone

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Hardcoded settings for testing
INFURA_API_KEY = "c592d537c4514e66b9af8b15770bc347"  # Already in settings.py
ETH_NETWORK_URL = f"https://sepolia.infura.io/v3/{INFURA_API_KEY}"
AUCTION_CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"  # Placeholder address

# Event signatures and ABIs from the original event_listener.py
EVENTS_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "auctionId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "seller",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "startingPrice",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "endTime",
                "type": "uint256"
            }
        ],
        "name": "AuctionCreated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "auctionId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "bidder",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "BidPlaced",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "auctionId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "winner",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "AuctionEnded",
        "type": "event"
    }
]

class SimpleEventListener:
    """Simplified event listener for testing."""
    
    def __init__(self, web3_provider=None, contract_address=None, block_interval=10):
        """Initialize the event listener."""
        self.web3_provider = web3_provider or ETH_NETWORK_URL
        self.contract_address = contract_address or AUCTION_CONTRACT_ADDRESS
        self.block_interval = block_interval
        self.w3 = None
        self.contract = None
        self.event_signatures = {}
        
        # Connect to Ethereum
        self._connect_to_ethereum()
    
    def _connect_to_ethereum(self):
        """Connect to Ethereum network."""
        try:
            logger.info(f"Connecting to Ethereum node at {self.web3_provider}...")
            self.w3 = Web3(Web3.HTTPProvider(self.web3_provider))
            
            if self.w3.is_connected():
                logger.info("✅ Successfully connected to Ethereum node!")
                
                try:
                    self.contract = self.w3.eth.contract(
                        address=self.w3.to_checksum_address(self.contract_address), 
                        abi=EVENTS_ABI
                    )
                    
                    # Manually define event signatures (topics) based on their hash
                    self.event_signatures = {
                        'AuctionCreated': self.w3.keccak(text="AuctionCreated(uint256,address,uint256,uint256)").hex(),
                        'BidPlaced': self.w3.keccak(text="BidPlaced(uint256,address,uint256)").hex(),
                        'AuctionEnded': self.w3.keccak(text="AuctionEnded(uint256,address,uint256)").hex()
                    }
                    
                    logger.info(f"Contract instance created for {self.contract_address}")
                    logger.info(f"AuctionCreated signature: {self.event_signatures['AuctionCreated']}")
                    logger.info(f"BidPlaced signature: {self.event_signatures['BidPlaced']}")
                    logger.info(f"AuctionEnded signature: {self.event_signatures['AuctionEnded']}")
                    return True
                except Exception as contract_error:
                    logger.error(f"Error creating contract instance: {contract_error}")
                    # Continue with connection but without contract instance
                    return True
            else:
                logger.error("Failed to connect to Ethereum node")
                return False
        except Exception as e:
            logger.error(f"Error connecting to Ethereum: {e}")
            return False
    
    def get_latest_block(self):
        """Get the latest block number."""
        try:
            return self.w3.eth.block_number
        except Exception as e:
            logger.error(f"Error getting latest block: {e}")
            return None
    
    def get_events(self, from_block, to_block):
        """Get events within a block range."""
        if not self.w3 or not self.w3.is_connected():
            logger.error("Not connected to Ethereum node")
            return []
        
        logger.info(f"Fetching events from block {from_block} to {to_block}")
        
        try:
            # Create filter
            event_filter = self.w3.eth.filter({
                'fromBlock': from_block,
                'toBlock': to_block,
                'address': self.w3.to_checksum_address(self.contract_address)
            })
            
            # Get logs
            logs = event_filter.get_all_entries()
            
            # Clean up filter
            self.w3.eth.uninstall_filter(event_filter.filter_id)
            
            # Process logs
            for log in logs:
                self._process_event(log)
                
            logger.info(f"Processed {len(logs)} events")
            return logs
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return []
    
    def _process_event(self, event):
        """Process a single event."""
        try:
            tx_hash = event['transactionHash'].hex()
            block_number = event['blockNumber']
            log_index = event['logIndex']
            
            # Get transaction timestamp
            block = self.w3.eth.get_block(block_number)
            timestamp = datetime.fromtimestamp(block['timestamp'], tz=timezone.utc)
            
            # Determine event type
            event_signature = event['topics'][0].hex()
            
            logger.info(f"Processing event: {event_signature} in block {block_number}, tx: {tx_hash}")
            
            if event_signature == self.event_signatures['AuctionCreated']:
                event_data = self.contract.events.AuctionCreated().process_log(event)
                logger.info(f"AuctionCreated: {event_data['args']}")
                
            elif event_signature == self.event_signatures['BidPlaced']:
                event_data = self.contract.events.BidPlaced().process_log(event)
                logger.info(f"BidPlaced: {event_data['args']}")
                
            elif event_signature == self.event_signatures['AuctionEnded']:
                event_data = self.contract.events.AuctionEnded().process_log(event)
                logger.info(f"AuctionEnded: {event_data['args']}")
            
            else:
                logger.info(f"Unknown event signature: {event_signature}")
        
        except Exception as e:
            logger.error(f"Error processing event: {e}")
    
    def run_test(self):
        """Run a test of the event listener."""
        if not self.w3 or not self.w3.is_connected():
            logger.error("Cannot test event listener - not connected to Ethereum node")
            return False
        
        latest_block = self.get_latest_block()
        if latest_block is None:
            logger.error("Cannot get latest block")
            return False
        
        # Check for events in the last 100 blocks
        from_block = max(0, latest_block - 100)
        
        logger.info(f"Checking for events from block {from_block} to {latest_block}")
        events = self.get_events(from_block, latest_block)
        
        if events:
            logger.info(f"Found {len(events)} events")
        else:
            logger.info("No events found in the specified block range")
            logger.info("This is normal if no auctions have been created on this contract or if the contract address is a placeholder")
        
        return True

# Run the test
if __name__ == "__main__":
    logger.info("Initializing event listener test...")
    listener = SimpleEventListener()
    
    if listener.w3 and listener.w3.is_connected():
        logger.info(f"Latest block number: {listener.get_latest_block()}")
        listener.run_test()
    else:
        logger.error("Failed to initialize event listener - connection failed")
    
    logger.info("Test completed")
    print("\nFollow the instructions in ethereum/README_ETHEREUM_SETUP.md if you encounter any issues.") 
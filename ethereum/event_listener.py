"""
Event listener module for Ethereum blockchain events.
This module monitors the Ethereum blockchain for auction events and updates the database.
"""

import logging
import time
from web3 import Web3
from web3.exceptions import BlockNotFound
from web3._utils.filters import LogFilter
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from requests.exceptions import ConnectionError, Timeout

from auctions.models import Auction, EthAuction, EthBid

logger = logging.getLogger(__name__)

class EventListener:
    """Event listener for Ethereum auction contract events."""
    
    def __init__(self, web3_provider=None, contract_address=None, block_interval=5, poll_interval=15, max_retries=3, retry_delay=5):
        """
        Initialize the event listener.
        
        Args:
            web3_provider: Web3 provider URL (default: settings.ETH_NETWORK_URL)
            contract_address: Auction contract address (default: settings.AUCTION_CONTRACT_ADDRESS)
            block_interval: Number of blocks to process in each batch
            poll_interval: Time in seconds to wait between polling
            max_retries: Maximum number of retries for connection issues
            retry_delay: Delay in seconds between retries
        """
        self.web3_provider = web3_provider or settings.ETH_NETWORK_URL
        self.contract_address = contract_address or settings.AUCTION_CONTRACT_ADDRESS
        self.block_interval = block_interval
        self.poll_interval = poll_interval
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.w3 = None
        
        # Connect to Ethereum node
        self._connect_to_ethereum()
        
        # ABI for the events we're interested in
        self.events_abi = [
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
        
        # Create contract instance
        if self.w3 and self.w3.is_connected():
            self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(self.contract_address), abi=self.events_abi)
            
            # Event signatures
            self.event_signatures = {
                'AuctionCreated': self.contract.events.AuctionCreated._get_event_abi()['signature'],
                'BidPlaced': self.contract.events.BidPlaced._get_event_abi()['signature'],
                'AuctionEnded': self.contract.events.AuctionEnded._get_event_abi()['signature']
            }
            
            logger.info(f"Event listener initialized for contract {self.contract_address}")
        else:
            logger.error("Failed to initialize event listener - unable to connect to Ethereum node")
    
    def _connect_to_ethereum(self):
        """Connect to Ethereum node with retry mechanism."""
        attempts = 0
        
        while attempts < self.max_retries:
            try:
                logger.info(f"Connecting to Ethereum node at {self.web3_provider}")
                self.w3 = Web3(Web3.HTTPProvider(self.web3_provider))
                
                if self.w3.is_connected():
                    logger.info("Successfully connected to Ethereum node")
                    return True
                else:
                    logger.warning("Failed to connect to Ethereum node")
            except (ConnectionError, Timeout) as e:
                logger.error(f"Connection error: {str(e)}")
            
            attempts += 1
            if attempts < self.max_retries:
                logger.info(f"Retrying in {self.retry_delay} seconds... (Attempt {attempts+1}/{self.max_retries})")
                time.sleep(self.retry_delay)
        
        logger.error(f"Failed to connect to Ethereum node after {self.max_retries} attempts")
        return False
    
    def get_latest_block(self):
        """Get the latest block number."""
        try:
            if not self.w3 or not self.w3.is_connected():
                if not self._connect_to_ethereum():
                    return None
            
            return self.w3.eth.block_number
        except Exception as e:
            logger.error(f"Error getting latest block: {e}")
            return None
    
    def get_last_synced_block(self):
        """Get the last synced block number from the database."""
        try:
            last_block = EthAuction.objects.order_by('-last_sync_block').first()
            if last_block:
                return last_block.last_sync_block
        except Exception as e:
            logger.error(f"Error getting last synced block: {e}")
        
        # If no blocks have been synced yet, start from the current block
        current_block = self.get_latest_block()
        logger.info(f"No previous sync data found, starting from current block {current_block}")
        return current_block
    
    def process_auction_created_event(self, event_data, block_number, tx_hash, timestamp):
        """Process AuctionCreated event."""
        logger.info(f"Processing AuctionCreated event: {event_data}")
        
        auction_id = event_data['args']['auctionId']
        seller = event_data['args']['seller']
        starting_price = event_data['args']['startingPrice']
        end_time = event_data['args']['endTime']
        
        # Convert end_time from Unix timestamp to datetime
        end_datetime = datetime.fromtimestamp(end_time)
        
        with transaction.atomic():
            # Check if we already have a Django auction with this ID
            # In a real implementation, you'd need a way to map on-chain IDs to Django IDs
            # For simplicity, we'll just use the auction_id as the Django ID
            try:
                auction = Auction.objects.get(id=auction_id)
                
                # Create EthAuction record
                eth_auction, created = EthAuction.objects.update_or_create(
                    auction=auction,
                    defaults={
                        'contract_address': self.contract_address,
                        'contract_auction_id': auction_id,
                        'seller_address': seller,
                        'start_block': block_number,
                        'last_sync_block': block_number
                    }
                )
                
                if created:
                    logger.info(f"Created EthAuction record for auction {auction_id}")
                else:
                    logger.info(f"Updated EthAuction record for auction {auction_id}")
                    
            except Auction.DoesNotExist:
                logger.warning(f"Django auction not found for on-chain auction {auction_id}")
    
    def process_bid_placed_event(self, event_data, block_number, tx_hash, timestamp):
        """Process BidPlaced event."""
        logger.info(f"Processing BidPlaced event: {event_data}")
        
        auction_id = event_data['args']['auctionId']
        bidder = event_data['args']['bidder']
        amount = event_data['args']['amount']
        
        with transaction.atomic():
            # Find the corresponding EthAuction
            try:
                eth_auction = EthAuction.objects.get(
                    contract_address=self.contract_address,
                    contract_auction_id=auction_id
                )
                
                # Create EthBid record
                eth_bid, created = EthBid.objects.update_or_create(
                    transaction_hash=tx_hash,
                    defaults={
                        'eth_auction': eth_auction,
                        'bidder_address': bidder,
                        'amount_wei': str(amount),
                        'block_number': block_number,
                        'timestamp': timestamp
                    }
                )
                
                if created:
                    logger.info(f"Created EthBid record for auction {auction_id}, bidder {bidder}, amount {amount}")
                
                # Update the Django auction's current price
                django_auction = eth_auction.auction
                from decimal import Decimal
                eth_amount = Decimal(amount) / Decimal(10**18)
                # In a real implementation, you'd convert ETH to USD based on current rates
                usd_amount = eth_amount * 3000  # Assuming 1 ETH = $3000
                
                # Update only if the new bid is higher
                if usd_amount > django_auction.current_price:
                    django_auction.current_price = usd_amount
                    django_auction.save(update_fields=['current_price'])
                    logger.info(f"Updated Django auction current price to ${usd_amount}")
                
                # Update last_sync_block
                eth_auction.last_sync_block = block_number
                eth_auction.save(update_fields=['last_sync_block'])
                
            except EthAuction.DoesNotExist:
                logger.warning(f"EthAuction not found for auction {auction_id}")
    
    def process_auction_ended_event(self, event_data, block_number, tx_hash, timestamp):
        """Process AuctionEnded event."""
        logger.info(f"Processing AuctionEnded event: {event_data}")
        
        auction_id = event_data['args']['auctionId']
        winner = event_data['args']['winner']
        amount = event_data['args']['amount']
        
        with transaction.atomic():
            # Find the corresponding EthAuction
            try:
                eth_auction = EthAuction.objects.get(
                    contract_address=self.contract_address,
                    contract_auction_id=auction_id
                )
                
                # Update EthAuction record
                eth_auction.end_block = block_number
                eth_auction.last_sync_block = block_number
                eth_auction.save(update_fields=['end_block', 'last_sync_block'])
                
                # Update Django auction
                django_auction = eth_auction.auction
                django_auction.status = 'CLOSED'
                
                # In a real implementation, you'd map Ethereum addresses to Django users
                # For simplicity, we won't update the winner field, as it requires a User object
                
                django_auction.save(update_fields=['status'])
                
                logger.info(f"Updated auction {auction_id} as closed, winner: {winner}")
                
            except EthAuction.DoesNotExist:
                logger.warning(f"EthAuction not found for auction {auction_id}")
    
    def process_event(self, event):
        """Process a single event."""
        # Get event details
        tx_hash = event['transactionHash'].hex()
        block_number = event['blockNumber']
        log_index = event['logIndex']
        
        # Get transaction timestamp
        block = self.w3.eth.get_block(block_number)
        timestamp = timezone.make_aware(datetime.fromtimestamp(block['timestamp']))
        
        # Determine event type
        event_signature = event['topics'][0].hex()
        
        try:
            if event_signature == self.event_signatures['AuctionCreated']:
                event_data = self.contract.events.AuctionCreated().process_log(event)
                self.process_auction_created_event(event_data, block_number, tx_hash, timestamp)
                
            elif event_signature == self.event_signatures['BidPlaced']:
                event_data = self.contract.events.BidPlaced().process_log(event)
                self.process_bid_placed_event(event_data, block_number, tx_hash, timestamp)
                
            elif event_signature == self.event_signatures['AuctionEnded']:
                event_data = self.contract.events.AuctionEnded().process_log(event)
                self.process_auction_ended_event(event_data, block_number, tx_hash, timestamp)
                
            else:
                logger.debug(f"Ignoring unknown event signature: {event_signature}")
                
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            logger.error(f"Event data: {event}")
    
    def sync_events(self, from_block=None, to_block=None):
        """
        Sync events from the blockchain.
        
        Args:
            from_block: Starting block number (default: last synced block)
            to_block: Ending block number (default: latest block)
        """
        if not self.w3 or not self.w3.is_connected():
            if not self._connect_to_ethereum():
                logger.error("Cannot sync events - not connected to Ethereum node")
                return 0
        
        if from_block is None:
            from_block = self.get_last_synced_block()
            if from_block is None:
                logger.error("Cannot determine last synced block")
                return 0
        
        if to_block is None:
            to_block = self.get_latest_block()
            if to_block is None:
                logger.error("Cannot determine latest block")
                return 0
            
        # Limit batch size to reduce load
        if to_block - from_block > self.block_interval:
            to_block = from_block + self.block_interval
            
        if from_block >= to_block:
            logger.info(f"No new blocks to sync. Current block: {to_block}")
            return 0
            
        logger.info(f"Syncing events from block {from_block} to {to_block}")
        
        try:
            # Get all events for our contract in the block range
            event_filter = self.w3.eth.filter({
                'fromBlock': from_block,
                'toBlock': to_block,
                'address': self.w3.to_checksum_address(self.contract_address)
            })
            
            events = event_filter.get_all_entries()
            
            # Process each event
            for event in events:
                self.process_event(event)
                
            # Clean up the filter
            self.w3.eth.uninstall_filter(event_filter.filter_id)
            
            # Update the last synced block for all EthAuctions
            EthAuction.objects.filter(contract_address=self.contract_address).update(last_sync_block=to_block)
            
            logger.info(f"Synced {len(events)} events from blocks {from_block} to {to_block}")
            return len(events)
        except Exception as e:
            logger.error(f"Error syncing events: {e}")
            return 0
    
    def run(self, run_once=False):
        """
        Run the event listener continuously.
        
        Args:
            run_once: If True, run only once; otherwise, run continuously
        """
        logger.info(f"Starting event listener for contract {self.contract_address}")
        
        while True:
            try:
                # Ensure connection is active
                if not self.w3 or not self.w3.is_connected():
                    if not self._connect_to_ethereum():
                        logger.warning("Not connected to Ethereum node, will retry later")
                        time.sleep(self.poll_interval)
                        continue
                
                # Sync events
                self.sync_events()
                
                if run_once:
                    break
                    
                time.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
                time.sleep(self.poll_interval)
                
        logger.info("Event listener stopped") 
from django.core.management.base import BaseCommand
from django.utils import timezone
from auctions.models import Auction, EthAuction
from ethereum.eth_integration import sync_auction_with_blockchain
import time

class Command(BaseCommand):
    help = 'Syncs auctions with the blockchain, ensuring each has a valid blockchain auction'

    def add_arguments(self, parser):
        parser.add_argument('--auction_id', type=int, help='Specific auction ID to sync')
        parser.add_argument('--all', action='store_true', help='Sync all active auctions')

    def handle(self, *args, **options):
        auction_id = options.get('auction_id')
        sync_all = options.get('all')
        
        if auction_id:
            # Sync specific auction
            try:
                auction = Auction.objects.get(id=auction_id)
                self.sync_single_auction(auction)
            except Auction.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Auction with ID {auction_id} not found"))
        elif sync_all:
            # Sync all active auctions
            auctions = Auction.objects.filter(status='ACTIVE')
            self.stdout.write(f"Syncing {auctions.count()} active auctions...")
            
            for auction in auctions:
                self.sync_single_auction(auction)
        else:
            self.stdout.write(self.style.WARNING("Please specify either --auction_id or --all"))
    
    def sync_single_auction(self, auction):
        """Sync a single auction with the blockchain"""
        self.stdout.write(f"Syncing auction {auction.id}: {auction.title}")
        
        # Convert auction end_date to UNIX timestamp
        end_timestamp = int(auction.end_date.timestamp())
        
        # Call the sync function
        result = sync_auction_with_blockchain(auction.id, end_timestamp)
        
        if result['success']:
            self.stdout.write(self.style.SUCCESS(result['message']))
            
            # Update or create EthAuction record
            blockchain_auction_id = result['blockchain_auction_id']
            
            if blockchain_auction_id is not None:
                # Get seller address
                seller_address = "0x511eA741479E2afB2179a12e9b374F9EbABF5268"  # Default address
                
                try:
                    # Update or create EthAuction record
                    eth_auction, created = EthAuction.objects.update_or_create(
                        auction=auction,
                        defaults={
                            'contract_address': "0x6eF09D25cD8AAb5A835FF721a250D549DF94313c",  # Use your deployed contract address
                            'contract_auction_id': blockchain_auction_id,
                            'seller_address': seller_address,
                            'start_block': 0,  # Placeholder
                            'last_sync_block': 0  # Placeholder
                        }
                    )
                    
                    action = "Created" if created else "Updated"
                    self.stdout.write(self.style.SUCCESS(f"{action} EthAuction record with blockchain ID {blockchain_auction_id}"))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error updating EthAuction record: {e}"))
        else:
            self.stdout.write(self.style.ERROR(result['message'])) 
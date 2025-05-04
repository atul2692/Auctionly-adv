from django.core.management.base import BaseCommand
from django.utils import timezone
from auctions.models import Auction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Manually check for ended auctions and process them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auction-id',
            type=int,
            help='Process a specific auction by ID',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(f"Checking for ended auctions at {now} (IST)")
        )
        
        auction_id = options.get('auction_id')
        
        if auction_id:
            # Process a specific auction
            try:
                auction = Auction.objects.get(id=auction_id)
                self.stdout.write(f"Processing auction: {auction.id} - {auction.title}")
                
                if auction.is_ended and auction.status == 'ACTIVE' and not auction.is_notified:
                    result = auction.close_auction()
                    if result:
                        self.stdout.write(
                            self.style.SUCCESS(f"Successfully closed auction {auction_id}")
                        )
                        
                        if auction.winner:
                            self.stdout.write(
                                self.style.SUCCESS(f"Winner: {auction.winner.username}")
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f"No winner for auction {auction_id}")
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"Could not close auction {auction_id}")
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Auction {auction_id} is not eligible for closing. " +
                            f"Is ended: {auction.is_ended}, " +
                            f"Status: {auction.status}, " +
                            f"Is notified: {auction.is_notified}"
                        )
                    )
            except Auction.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Auction {auction_id} not found")
                )
        else:
            # Process all eligible auctions
            ended_auctions = Auction.objects.filter(
                status='ACTIVE',
                is_notified=False,
                end_date__lte=now
            )
            
            count = ended_auctions.count()
            if count == 0:
                self.stdout.write(
                    self.style.WARNING("No ended auctions found to process")
                )
                return
                
            self.stdout.write(
                self.style.SUCCESS(f"Found {count} ended auctions to process")
            )
            
            processed = 0
            for auction in ended_auctions:
                self.stdout.write(f"Processing: {auction.id} - {auction.title}")
                
                if auction.close_auction():
                    processed += 1
                    if auction.winner:
                        self.stdout.write(
                            self.style.SUCCESS(f"Winner: {auction.winner.username}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"No winner for auction {auction.id}")
                        )
            
            self.stdout.write(
                self.style.SUCCESS(f"Successfully processed {processed} of {count} auctions")
            ) 
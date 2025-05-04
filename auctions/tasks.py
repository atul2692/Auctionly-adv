from celery import shared_task
from django.utils import timezone
from .models import Auction
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_ended_auctions():
    """
    Celery task to check for ended auctions, set winners, and send notifications
    This runs every minute as scheduled in celery.py
    """
    # Get current time in India timezone (IST)
    now = timezone.now()
    logger.info(f"Checking for ended auctions at {now} (IST)")
    
    # Get all active auctions that have ended but haven't been processed
    ended_auctions = Auction.objects.filter(
        status='ACTIVE',
        is_notified=False,
        end_date__lte=now
    )
    
    auction_count = ended_auctions.count()
    if auction_count > 0:
        logger.info(f"Found {auction_count} ended auctions to process")
        
        # Process each ended auction
        for auction in ended_auctions:
            logger.info(f"Processing auction ID: {auction.id}, Title: {auction.title}")
            process_ended_auction.delay(auction.id)
    else:
        logger.info("No ended auctions found to process")
    
    return f"Processed {auction_count} ended auctions"

@shared_task
def process_ended_auction(auction_id):
    """
    Process a single ended auction - determine winner and send notifications
    """
    try:
        logger.info(f"Starting to process auction {auction_id}")
        auction = Auction.objects.get(id=auction_id)
        
        # Skip if already processed
        if auction.status == 'CLOSED' or auction.is_notified:
            logger.info(f"Auction {auction_id} already processed, skipping")
            return f"Auction {auction_id} already processed"
        
        # Skip if not ended yet (double check)
        if not auction.is_ended:
            logger.info(f"Auction {auction_id} has not ended yet, skipping")
            return f"Auction {auction_id} has not ended yet"
        
        # Close the auction and set the winner
        logger.info(f"Closing auction {auction_id} and determining winner")
        auction.close_auction()
        
        # Log the winner information
        if auction.winner:
            logger.info(f"Auction {auction_id} winner determined: {auction.winner.username}")
        else:
            logger.info(f"Auction {auction_id} ended with no winner")
        
        return f"Successfully processed auction {auction_id}"
    
    except Auction.DoesNotExist:
        logger.error(f"Auction {auction_id} not found")
        return f"Auction {auction_id} not found"
    except Exception as e:
        logger.error(f"Error processing auction {auction_id}: {str(e)}")
        return f"Error processing auction {auction_id}: {str(e)}" 
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import logging

class Category(models.Model):
    """
    Category model for auction listings
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('auctions:category_detail', args=[self.slug])


class Auction(models.Model):
    """
    Auction listing model
    """
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('PENDING', 'Pending Review'),
        ('CLOSED', 'Closed'),
    )
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auctions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='auctions')
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='auction_images/')
    additional_images = models.ManyToManyField('AuctionImage', blank=True, related_name='auctions_as_additional')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='won_auctions', null=True, blank=True)
    is_notified = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('auctions:auction_detail', args=[self.slug])
    
    @property
    def is_ended(self):
        return timezone.now() >= self.end_date
    
    @property
    def time_remaining(self):
        if self.is_ended:
            return "Auction ended"
        
        time_left = self.end_date - timezone.now()
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"
    
    @property
    def bid_count(self):
        return self.bids.count()
    
    @property
    def highest_bid(self):
        return self.bids.order_by('-amount').first()
    
    def close_auction(self):
        """
        Close the auction, set the winner, and send notifications
        """
        logger = logging.getLogger(__name__)
        
        if self.is_ended and self.status == 'ACTIVE' and not self.is_notified:
            logger.info(f"Closing auction: {self.id} - {self.title}")
            
            # Set status to closed
            self.status = 'CLOSED'
            
            # Set the winner if there are bids
            highest_bid = self.highest_bid
            if highest_bid:
                self.winner = highest_bid.bidder
                logger.info(f"Setting winner for auction {self.id}: {self.winner.username} with bid ${highest_bid.amount}")
                
                # Send notification emails
                logger.info(f"Sending notification emails for auction {self.id}")
                self.send_auction_end_notifications()
            else:
                logger.info(f"No bids found for auction {self.id}, no winner to set")
            
            self.is_notified = True
            self.save()
            logger.info(f"Auction {self.id} successfully closed and updated")
            return True
        
        logger.info(f"Auction {self.id} not ready to be closed or already closed")
        return False
    
    def send_auction_end_notifications(self):
        """
        Send notification emails to the winner and seller
        """
        logger = logging.getLogger(__name__)
        
        if not self.winner:
            logger.warning(f"Cannot send notifications for auction {self.id} - no winner")
            return False
        
        site_url = 'http://localhost:8000'  # Replace with your actual site URL in production
        auction_url = f"{site_url}{self.get_absolute_url()}"
        
        try:
            # Send email to winner
            logger.info(f"Sending winner notification email to {self.winner.email}")
            winner_subject = f"Congratulations! You won the auction for {self.title}"
            winner_message = render_to_string('auctions/emails/auction_won_email.html', {
                'auction': self,
                'user': self.winner,
                'bid_amount': self.current_price,
                'auction_url': auction_url,
                'timezone': 'IST'
            })
            
            winner_email = EmailMessage(
                subject=winner_subject,
                body=winner_message,
                from_email='management.auctionly@gmail.com',
                to=[self.winner.email]
            )
            winner_email.content_subtype = "html"
            winner_email.send()
            logger.info(f"Winner notification email sent to {self.winner.email}")
            
            # Send email to seller
            logger.info(f"Sending seller notification email to {self.seller.email}")
            seller_subject = f"Your auction for {self.title} has ended"
            seller_message = render_to_string('auctions/emails/auction_ended_email.html', {
                'auction': self,
                'user': self.seller,
                'winner': self.winner,
                'bid_amount': self.current_price,
                'auction_url': auction_url,
                'timezone': 'IST'
            })
            
            seller_email = EmailMessage(
                subject=seller_subject,
                body=seller_message,
                from_email='management.auctionly@gmail.com',
                to=[self.seller.email]
            )
            seller_email.content_subtype = "html"
            seller_email.send()
            logger.info(f"Seller notification email sent to {self.seller.email}")
            
            return True
        except Exception as e:
            logger.error(f"Error sending notification emails for auction {self.id}: {str(e)}")
            return False


class AuctionImage(models.Model):
    """
    Additional images for auction listings
    """
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='auction_images/')
    
    def __str__(self):
        return f"Image for {self.auction.title}"


class Bid(models.Model):
    """
    Bid model for auction listings
    """
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-amount']
    
    def __str__(self):
        return f"{self.bidder.username} bid ${self.amount} on {self.auction.title}"


class Watchlist(models.Model):
    """
    Watchlist model for users to save auctions they're interested in
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='watchlists')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'auction')
    
    def __str__(self):
        return f"{self.user.username}'s watchlist item: {self.auction.title}"


class EthPayment(models.Model):
    """
    Ethereum payment model for auction payments
    """
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='ethpayment')
    buyer_address = models.CharField(max_length=42)  # Ethereum address
    seller_address = models.CharField(max_length=42)  # Ethereum address
    usd_amount = models.DecimalField(max_digits=10, decimal_places=2)
    eth_amount_wei = models.CharField(max_length=78)  # Store as string to handle large numbers
    tx_hash = models.CharField(max_length=66)  # Ethereum transaction hash
    is_paid = models.BooleanField(default=False)
    payment_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment for {self.auction.title} - ${self.usd_amount}"
    
    @property
    def eth_amount(self):
        """Convert wei to ETH for display"""
        from decimal import Decimal
        return Decimal(self.eth_amount_wei) / Decimal(10**18)


class EthAuction(models.Model):
    """
    Model to track Ethereum auction data for analytics and notifications
    """
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='eth_auction')
    contract_address = models.CharField(max_length=42)  # Ethereum contract address
    contract_auction_id = models.PositiveIntegerField()  # ID of the auction in the smart contract (renamed from auction_id)
    seller_address = models.CharField(max_length=42)  # Ethereum address of the seller
    start_block = models.PositiveIntegerField()  # Block number when the auction was created
    end_block = models.PositiveIntegerField(null=True, blank=True)  # Block number when the auction ended
    last_sync_block = models.PositiveIntegerField()  # Last block that was synced
    
    def __str__(self):
        return f"ETH Auction {self.contract_auction_id} for {self.auction.title}"
    
    class Meta:
        indexes = [
            models.Index(fields=['contract_address', 'contract_auction_id']),
        ]


class EthBid(models.Model):
    """
    Model to track Ethereum bids for analytics and notifications
    """
    eth_auction = models.ForeignKey(EthAuction, on_delete=models.CASCADE, related_name='eth_bids')
    bidder_address = models.CharField(max_length=42)  # Ethereum address of the bidder
    amount_wei = models.CharField(max_length=78)  # Bid amount in wei (stored as string to handle large numbers)
    transaction_hash = models.CharField(max_length=66, unique=True)  # Transaction hash
    block_number = models.PositiveIntegerField()  # Block number of the transaction
    timestamp = models.DateTimeField()  # Timestamp of the bid
    
    def __str__(self):
        return f"ETH Bid: {self.bidder_address[:10]}... {self.eth_amount} ETH"
    
    @property
    def eth_amount(self):
        """Convert wei to ETH for display"""
        from decimal import Decimal
        return Decimal(self.amount_wei) / Decimal(10**18)
    
    class Meta:
        ordering = ['-block_number']
        indexes = [
            models.Index(fields=['bidder_address']),
            models.Index(fields=['block_number']),
        ]


class RazorpayPayment(models.Model):
    """
    Model to track Razorpay payments for auctions
    """
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='razorpay_payment')
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    receipt = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment for {self.auction.title} - {self.order_id}"

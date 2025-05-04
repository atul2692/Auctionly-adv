from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.urls import reverse
import uuid
import logging
import razorpay
import json
from django.views.decorators.csrf import csrf_exempt
from .models import RazorpayPayment
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .models import Auction, Category, Bid, Watchlist, AuctionImage
from .forms import AuctionForm, BidForm, AuctionImageForm

def auction_list(request):
    """
    View for listing all active auctions
    """
    category_slug = request.GET.get('category')
    query = request.GET.get('q')
    sort = request.GET.get('sort', '-created_at')
    
    auctions = Auction.objects.filter(status='ACTIVE')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        auctions = auctions.filter(category=category)
    
    if query:
        auctions = auctions.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
        
    # Sorting
    if sort == 'price_low':
        auctions = auctions.order_by('current_price')
    elif sort == 'price_high':
        auctions = auctions.order_by('-current_price')
    elif sort == 'ending_soon':
        auctions = auctions.order_by('end_date')
    elif sort == 'newest':
        auctions = auctions.order_by('-created_at')
        
    # Get all categories for the sidebar
    categories = Category.objects.all()
    
    # Setup pagination
    paginator = Paginator(auctions, 12)  # Show 12 auctions per page
    page_number = request.GET.get('page')
    auctions_page = paginator.get_page(page_number)
    
    context = {
        'auctions': auctions_page,
        'categories': categories,
        'active_category': category_slug,
        'query': query,
        'sort': sort,
    }
    
    return render(request, 'auctions/auction_list.html', context)


def auction_detail(request, slug):
    """
    View for auction details
    """
    auction = get_object_or_404(Auction, slug=slug)
    
    # Check if auction has ended using server-side logic
    # This will ensure the auction status is updated on each page view
    if auction.is_ended and auction.status == 'ACTIVE' and not auction.is_notified:
        try:
            # Process the auction directly instead of using Celery
            auction.close_auction()
        except Exception as e:
            messages.error(request, f"Error processing ended auction: {str(e)}")
    
    # Increment view count
    auction.views_count += 1
    auction.save(update_fields=['views_count'])
    
    # Check if auction is in user's watchlist
    is_in_watchlist = False
    if request.user.is_authenticated:
        is_in_watchlist = Watchlist.objects.filter(user=request.user, auction=auction).exists()
    
    # Get bid history
    bids = auction.bids.all()[:10]  # Limited to the most recent 10 bids
    
    # Get bid form
    bid_form = BidForm(auction=auction)
    
    # Get related auctions
    related_auctions = Auction.objects.filter(
        category=auction.category, 
        status='ACTIVE'
    ).exclude(id=auction.id)[:4]
    
    # Calculate minimum ETH bid (current USD price converted to ETH)
    from ethereum.eth_integration import usd_to_eth
    from decimal import Decimal
    
    try:
        # Convert USD to ETH for minimum bid
        usd_amount = float(auction.current_price)
        eth_amount_wei = usd_to_eth(usd_amount)
        eth_min_bid = float(eth_amount_wei) / 10**18  # Convert wei to ETH
        
        # Add 1% to ensure it's higher than the current bid
        eth_min_bid = round(eth_min_bid * 1.01, 4)
    except Exception as e:
        # Use fallback conversion if eth_integration fails
        eth_min_bid = round(float(auction.current_price) / 3000.0, 4)  # Simple $3000 per ETH conversion
    
    # Get contract address from settings
    contract_address = getattr(settings, 'AUCTION_CONTRACT_ADDRESS', '0x1234567890123456789012345678901234567890')
    
    context = {
        'auction': auction,
        'bids': bids,
        'bid_form': bid_form,
        'is_in_watchlist': is_in_watchlist,
        'related_auctions': related_auctions,
        'eth_min_bid': eth_min_bid,
        'auction_contract_address': contract_address,
    }
    
    return render(request, 'auctions/auction_detail.html', context)


@login_required
def create_auction(request):
    """
    View for creating a new auction
    """
    # Check if user is a seller
    if not request.user.is_seller:
        messages.error(request, 'Only sellers can create auction listings.')
        return redirect('home:index')
    
    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.seller = request.user
            
            # Create a unique slug by adding a short UUID suffix
            base_slug = slugify(auction.title)
            unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
            auction.slug = f"{base_slug}-{unique_id}"
            
            auction.current_price = auction.starting_price
            auction.status = 'ACTIVE'  # Automatically activate for now, can be changed to PENDING for moderation
            auction.save()
            
            # Handle additional images
            images = request.FILES.getlist('additional_images')
            for img in images:
                auction_image = AuctionImage(auction=auction, image=img)
                auction_image.save()
                
            messages.success(request, 'Your auction has been created and is now live!')
            return redirect('auctions:auction_detail', slug=auction.slug)
    else:
        form = AuctionForm()
    
    context = {
        'form': form,
        'title': 'Create New Auction'
    }
    
    return render(request, 'auctions/auction_form.html', context)


@login_required
def edit_auction(request, slug):
    """
    View for editing an existing auction
    """
    auction = get_object_or_404(Auction, slug=slug)
    
    # Check if user is the seller
    if request.user != auction.seller:
        messages.error(request, 'You can only edit your own auctions.')
        return redirect('auctions:auction_detail', slug=auction.slug)
    
    # Check if auction is still active
    if auction.status != 'ACTIVE':
        messages.error(request, 'You can only edit active auctions.')
        return redirect('auctions:auction_detail', slug=auction.slug)
    
    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES, instance=auction)
        if form.is_valid():
            form.save()
            
            # Handle additional images
            images = request.FILES.getlist('additional_images')
            for img in images:
                auction_image = AuctionImage(auction=auction, image=img)
                auction_image.save()
                
            messages.success(request, 'Your auction has been updated!')
            return redirect('auctions:auction_detail', slug=auction.slug)
    else:
        form = AuctionForm(instance=auction)
    
    context = {
        'form': form,
        'auction': auction,
        'title': 'Edit Auction'
    }
    
    return render(request, 'auctions/auction_form.html', context)


@login_required
@require_POST
def place_bid(request, slug):
    """
    View for placing a bid on an auction
    """
    auction = get_object_or_404(Auction, slug=slug)
    
    # Check if auction has ended
    if auction.is_ended:
        if auction.status == 'ACTIVE' and not auction.is_notified:
            try:
                # Process the auction directly instead of using Celery
                auction.close_auction()
            except Exception as e:
                messages.error(request, f"Error processing ended auction: {str(e)}")
        messages.error(request, 'This auction has ended.')
        return redirect('auctions:auction_detail', slug=auction.slug)
    
    # Check if auction is active
    if auction.status != 'ACTIVE':
        messages.error(request, 'This auction is not active.')
        return redirect('auctions:auction_detail', slug=auction.slug)
    
    # Check if user is the seller
    if request.user == auction.seller:
        messages.error(request, 'You cannot bid on your own auction.')
        return redirect('auctions:auction_detail', slug=auction.slug)
    
    form = BidForm(request.POST, auction=auction, user=request.user)
    
    if form.is_valid():
        bid = form.save(commit=False)
        bid.auction = auction
        bid.bidder = request.user
        bid.save()
        
        # Update the current price
        auction.current_price = bid.amount
        auction.save(update_fields=['current_price'])
        
        messages.success(request, f'Your bid of ${bid.amount} has been placed!')
        
        # If AJAX request, return JSON response
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'Your bid of ${bid.amount} has been placed!',
                'new_price': float(auction.current_price),
                'bid_count': auction.bid_count,
            })
    else:
        messages.error(request, form.errors.get('amount', 'Invalid bid amount.'))
        
        # If AJAX request, return JSON response
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': form.errors.get('amount', 'Invalid bid amount.'),
            })
    
    return redirect('auctions:auction_detail', slug=auction.slug)


@login_required
def toggle_watchlist(request, slug):
    """
    View for adding/removing auctions from watchlist
    """
    auction = get_object_or_404(Auction, slug=slug)
    watchlist_item, created = Watchlist.objects.get_or_create(user=request.user, auction=auction)
    
    if not created:
        # Item already exists, remove it
        watchlist_item.delete()
        is_in_watchlist = False
        message = f'{auction.title} has been removed from your watchlist.'
    else:
        is_in_watchlist = True
        message = f'{auction.title} has been added to your watchlist.'
    
    messages.success(request, message)
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'in_watchlist': is_in_watchlist,
            'message': message,
        })
    
    return redirect('auctions:auction_detail', slug=auction.slug)


@login_required
def watchlist(request):
    """
    View for user's watchlist
    """
    watched_items = Watchlist.objects.filter(user=request.user).select_related('auction').order_by('-added_at')
    
    context = {
        'watched_items': watched_items,
    }
    
    return render(request, 'auctions/watchlist.html', context)


@login_required
def my_auctions(request):
    """
    View for user's auctions
    """
    # Check if user is a seller
    if not request.user.is_seller:
        messages.error(request, 'Only sellers can view their auctions.')
        return redirect('home:index')
    
    auctions = request.user.auctions.all().order_by('-created_at')
    
    context = {
        'auctions': auctions,
    }
    
    return render(request, 'auctions/my_auctions.html', context)


@login_required
def my_bids(request):
    """
    View for user's bids
    """
    bids = Bid.objects.filter(bidder=request.user).select_related('auction').order_by('-created_at')
    
    context = {
        'bids': bids,
    }
    
    return render(request, 'auctions/my_bids.html', context)


def categories(request):
    """
    View for all categories
    """
    categories = Category.objects.annotate(
        active_auction_count=Count(
            'auctions',
            filter=Q(auctions__status='ACTIVE')
        )
    )
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'auctions/categories.html', context)


def category_detail(request, slug):
    """
    View for a specific category
    """
    category = get_object_or_404(Category, slug=slug)
    auctions = Auction.objects.filter(category=category, status='ACTIVE')
    
    # Setup pagination
    paginator = Paginator(auctions, 12)  # Show 12 auctions per page
    page_number = request.GET.get('page')
    auctions_page = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'auctions': auctions_page,
    }
    
    return render(request, 'auctions/category_detail.html', context)


@login_required
def delete_auction(request, slug):
    """
    View for deleting an auction (seller only)
    """
    auction = get_object_or_404(Auction, slug=slug)
    
    # Check if user is the seller
    if request.user != auction.seller:
        messages.error(request, 'You can only delete your own auctions.')
        return redirect('auctions:auction_detail', slug=auction.slug)
    
    # If this is a POST request, delete the auction
    if request.method == 'POST':
        auction_title = auction.title
        
        # First try to delete any related EthAuction records
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auctions_ethauction'")
            if cursor.fetchone():
                # Table exists, so check if there's a record for this auction
                from auctions.models import EthAuction
                try:
                    eth_auction = EthAuction.objects.filter(auction=auction).first()
                    if eth_auction:
                        eth_auction.delete()
                except Exception as e:
                    # Log the error but continue
                    print(f"Error deleting related EthAuction: {e}")
        except Exception as e:
            # Log the error but continue with auction deletion
            print(f"Error checking for EthAuction table: {e}")
        
        # Now delete the auction
        try:
            auction.delete()
            messages.success(request, f'Your auction "{auction_title}" has been deleted.')
        except Exception as e:
            messages.error(request, f'Error deleting auction: {e}')
        
        return redirect('auctions:my_auctions')
    
    # If this is a GET request, show confirmation page
    context = {
        'auction': auction,
    }
    
    return render(request, 'auctions/delete_auction_confirm.html', context)


@login_required
@require_POST
def delete_auction_image(request, pk):
    """
    View for deleting an auction image
    """
    image = get_object_or_404(AuctionImage, pk=pk)
    auction = image.auction
    
    # Check if user is the seller
    if request.user != auction.seller:
        return JsonResponse({'status': 'error', 'message': 'You can only delete images from your own auctions.'}, status=403)
    
    # Check if auction is still active
    if auction.status != 'ACTIVE':
        return JsonResponse({'status': 'error', 'message': 'You can only modify active auctions.'}, status=403)
    
    try:
        # Delete the image
        image.delete()
        return JsonResponse({'status': 'success', 'message': 'Image deleted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def process_ended_auction(request, slug):
    """
    API endpoint to process an ended auction and determine the winner
    Called by JavaScript when an auction's timer ends in the browser
    """
    try:
        auction = get_object_or_404(Auction, slug=slug)
        
        # Check if the auction has already ended
        if auction.status == 'CLOSED' or auction.is_notified:
            return JsonResponse({
                'success': True,
                'message': 'Auction already processed',
                'winner': auction.winner.username if auction.winner else None
            })
        
        # Check if the auction end date has passed
        if timezone.now() >= auction.end_date:
            # Close the auction and set the winner
            result = auction.close_auction()
            
            if result:
                # Return more detailed success information
                return JsonResponse({
                    'success': True,
                    'message': 'Auction processed successfully',
                    'winner': auction.winner.username if auction.winner else None,
                    'bid_amount': str(auction.current_price) if auction.winner else None,
                    'status': auction.status,
                    'notifications_sent': auction.is_notified
                })
            else:
                # Return more detailed error information
                return JsonResponse({
                    'success': False,
                    'message': 'Auction could not be processed',
                    'reason': 'The auction may already be closed or there was an error processing it'
                })
        else:
            # Auction hasn't actually ended yet
            time_remaining = auction.end_date - timezone.now()
            seconds_remaining = int(time_remaining.total_seconds())
            
            return JsonResponse({
                'success': False,
                'message': 'Auction has not ended yet',
                'seconds_remaining': seconds_remaining,
                'should_refresh': seconds_remaining < 5  # Suggest refresh if very close to ending
            })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        # Log the detailed error
        logger = logging.getLogger(__name__)
        logger.error(f"Error processing auction {slug}: {str(e)}\n{error_details}")
        
        return JsonResponse({
            'success': False,
            'message': f'Error processing auction: {str(e)}',
            'error_type': e.__class__.__name__
        })


@login_required
def razorpay_payment(request, slug):
    """
    View for creating Razorpay payment for a won auction
    """
    auction = get_object_or_404(Auction, slug=slug)
    
    # Check if user is the winner
    if request.user != auction.winner:
        messages.error(request, 'Only the auction winner can make a payment.')
        return redirect('auctions:auction_detail', slug=auction.slug)
    
    # Check if auction is already paid
    if auction.is_paid:
        messages.info(request, 'This auction has already been paid for.')
        return redirect('auctions:auction_detail', slug=auction.slug)
    
    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Create a new payment order if it doesn't exist
    if not hasattr(auction, 'razorpay_payment'):
        # Convert amount to paise (Razorpay expects amount in smallest currency unit)
        amount_in_paise = int(float(auction.current_price) * 100)
        
        # Create Razorpay order
        data = {
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': f'receipt_auction_{auction.id}',
            'notes': {
                'auction_id': auction.id,
                'title': auction.title,
                'winner': request.user.username
            }
        }
        
        try:
            # Create the order
            razorpay_order = client.order.create(data=data)
            
            # Save order details to database
            payment = RazorpayPayment.objects.create(
                auction=auction,
                order_id=razorpay_order['id'],
                amount=auction.current_price,
                receipt=data['receipt']
            )
        except Exception as e:
            messages.error(request, f'Error creating payment: {str(e)}')
            return redirect('auctions:auction_detail', slug=auction.slug)
    else:
        # Use existing payment
        payment = auction.razorpay_payment
        
        # Check if order needs to be fetched again
        try:
            razorpay_order = client.order.fetch(payment.order_id)
        except Exception as e:
            messages.error(request, f'Error fetching payment: {str(e)}')
            return redirect('auctions:auction_detail', slug=auction.slug)
    
    context = {
        'auction': auction,
        'payment': payment,
        'razorpay_order_id': payment.order_id,
        'razorpay_amount': int(float(payment.amount) * 100),  # Convert to paise
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'callback_url': request.build_absolute_uri(reverse('auctions:razorpay_callback', kwargs={'slug': auction.slug})),
        'prefill': {
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'contact': getattr(request.user, 'phone_number', '')
        }
    }
    
    return render(request, 'auctions/razorpay_payment.html', context)


@csrf_exempt
@require_POST
def razorpay_callback(request, slug):
    """
    Callback endpoint for Razorpay to verify payment
    """
    auction = get_object_or_404(Auction, slug=slug)
    
    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Get payment data from POST request
    try:
        data = json.loads(request.body)
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')
        
        # Verify the payment signature
        params_dict = {
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_signature': razorpay_signature
        }
        
        # Verify signature
        client.utility.verify_payment_signature(params_dict)
        
        # Update payment status
        payment = get_object_or_404(RazorpayPayment, order_id=razorpay_order_id)
        payment.payment_id = razorpay_payment_id
        payment.status = 'successful'
        payment.save()
        
        # Mark auction as paid
        auction.is_paid = True
        auction.save()
        
        # Send payment confirmation emails
        send_payment_confirmation_emails(auction)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Payment successful',
            'redirect_url': reverse('auctions:auction_detail', kwargs={'slug': auction.slug})
        })
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error processing Razorpay payment: {str(e)}")
        
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


def send_payment_confirmation_emails(auction):
    """
    Send payment confirmation emails to the winner and seller
    """
    logger = logging.getLogger(__name__)
    
    if not auction.winner:
        logger.warning(f"Cannot send payment confirmations for auction {auction.id} - no winner")
        return False
    
    site_url = 'http://localhost:8000'  # Replace with actual site URL in production
    auction_url = f"{site_url}{auction.get_absolute_url()}"
    
    try:
        # Send email to winner
        logger.info(f"Sending payment confirmation email to winner {auction.winner.email}")
        winner_subject = f"Payment Confirmation - {auction.title}"
        winner_message = render_to_string('auctions/emails/payment_confirmation_buyer.html', {
            'auction': auction,
            'user': auction.winner,
            'payment_amount': auction.current_price,
            'auction_url': auction_url,
            'timezone': 'IST'
        })
        
        winner_email = EmailMessage(
            subject=winner_subject,
            body=winner_message,
            from_email='management.auctionly@gmail.com',
            to=[auction.winner.email]
        )
        winner_email.content_subtype = "html"
        winner_email.send()
        
        # Send email to seller
        logger.info(f"Sending payment confirmation email to seller {auction.seller.email}")
        seller_subject = f"Payment Received - {auction.title}"
        seller_message = render_to_string('auctions/emails/payment_confirmation_seller.html', {
            'auction': auction,
            'user': auction.seller,
            'winner': auction.winner,
            'payment_amount': auction.current_price,
            'auction_url': auction_url,
            'timezone': 'IST'
        })
        
        seller_email = EmailMessage(
            subject=seller_subject,
            body=seller_message,
            from_email='management.auctionly@gmail.com',
            to=[auction.seller.email]
        )
        seller_email.content_subtype = "html"
        seller_email.send()
        
        return True
    except Exception as e:
        logger.error(f"Error sending payment confirmation emails for auction {auction.id}: {str(e)}")
        return False

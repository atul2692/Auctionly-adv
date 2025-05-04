from django.shortcuts import render, redirect
from auctions.models import Auction, Category
from django.db.models import Count
import random
from django.contrib import messages

# Create your views here.

def index(request):
    """
    View for the landing page
    """
    # Get active auctions
    active_auctions = list(Auction.objects.filter(status='ACTIVE'))
    
    # Randomly select 4 featured auctions from active auctions
    featured_auctions = []
    if len(active_auctions) > 4:
        featured_auctions = random.sample(active_auctions, 4)
    else:
        featured_auctions = active_auctions
    
    # Get recent auctions
    recent_auctions = Auction.objects.filter(status='ACTIVE').order_by('-created_at')[:8]
    
    # Get popular categories
    categories = Category.objects.all()[:6]
    
    context = {
        'featured_auctions': featured_auctions,
        'recent_auctions': recent_auctions,
        'categories': categories,
    }
    
    return render(request, 'home/index.html', context)

def contact(request):
    """
    View for the contact page
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you would typically send an email or save to database
        # For now, we'll just show a success message
        
        messages.success(request, 'Your message has been sent successfully. We\'ll get back to you soon!')
        return redirect('home:contact')
    
    return render(request, 'home/contact.html')

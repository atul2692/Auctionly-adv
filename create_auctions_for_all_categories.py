import os
import django
import random
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_site.settings')
django.setup()

from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from auctions.models import Category, Auction
from fix_auctions import ensure_media_dirs, create_dummy_image

User = get_user_model()

def create_auction_for_category(category, seller):
    """Create a sample auction for a specific category"""
    # Ensure directories exist
    auction_images_dir = ensure_media_dirs()
    
    # Create sample auction data
    title = f"{category.name} Item {random.randint(1000, 9999)}"
    slug = slugify(title)
    
    # Check if this auction already exists
    if Auction.objects.filter(slug=slug).exists():
        print(f"Auction with title '{title}' already exists. Skipping.")
        return None
    
    # Create a dummy image
    image_filename = f"{slug}.png"
    image_path = create_dummy_image(auction_images_dir, image_filename)
    
    if not image_path:
        print(f"Failed to create image for '{title}'. Skipping auction.")
        return None
    
    # Random data
    end_date = timezone.now() + timedelta(days=random.randint(3, 14))
    starting_price = round(random.uniform(19.99, 999.99), 2)
    description = f"""
This is an amazing {category.name} item up for auction!

• High quality
• Excellent condition
• Carefully packaged
• Fast shipping

Don't miss your chance to own this fantastic item from our {category.name} collection!
    """
    
    # Create the auction
    try:
        auction = Auction.objects.create(
            title=title,
            slug=slug,
            seller=seller,
            category=category,
            description=description,
            starting_price=starting_price,
            current_price=starting_price,
            end_date=end_date,
            status='ACTIVE',
            featured=(random.random() > 0.7),  # 30% chance of being featured
            image=f"auction_images/{image_filename}"
        )
        
        print(f"Created auction: {title}")
        print(f"Category: {category.name}")
        print(f"Starting price: ${starting_price}")
        print(f"End date: {end_date}")
        print(f"Featured: {auction.featured}")
        
        return auction
    except Exception as e:
        print(f"Error creating auction for category {category.name}: {e}")
        return None

def create_auctions_for_all_categories():
    """Create auctions for all existing categories"""
    # Get the admin user
    try:
        admin = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("Admin user not found. Please create an admin user first.")
        return
    
    # Get all categories
    categories = Category.objects.all()
    
    if not categories.exists():
        print("No categories found. Please create categories first.")
        return
    
    print(f"Found {categories.count()} categories. Creating auctions...")
    
    # Create 2 auctions for each category
    for category in categories:
        print(f"\nProcessing category: {category.name}")
        
        for i in range(2):
            create_auction_for_category(category, admin)
            
    print("\nFinished creating auctions for all categories.")

if __name__ == "__main__":
    create_auctions_for_all_categories() 
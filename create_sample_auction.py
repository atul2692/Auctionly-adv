import os
import django
from datetime import datetime, timedelta
import random
import urllib.request
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_site.settings')
django.setup()

from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model
from auctions.models import Category, Auction

User = get_user_model()

# Placeholder images for different categories
PLACEHOLDER_IMAGES = {
    'electronics': 'https://via.placeholder.com/600x400.png?text=Electronics+Item',
    'collectibles': 'https://via.placeholder.com/600x400.png?text=Collectible+Item',
    'fashion': 'https://via.placeholder.com/600x400.png?text=Fashion+Item',
    'home & garden': 'https://via.placeholder.com/600x400.png?text=Home+and+Garden+Item',
    'art': 'https://via.placeholder.com/600x400.png?text=Art+Item',
    'vehicles': 'https://via.placeholder.com/600x400.png?text=Vehicle+Item',
    'jewelry': 'https://via.placeholder.com/600x400.png?text=Jewelry+Item',
    'sports': 'https://via.placeholder.com/600x400.png?text=Sports+Item',
    'default': 'https://via.placeholder.com/600x400.png?text=Auction+Item',
}

def get_image_from_url(url):
    try:
        # Create a temporary file
        img_temp = NamedTemporaryFile(delete=True)
        
        # Get the image from the URL
        urllib.request.urlretrieve(url, img_temp.name)
        
        # Return the file
        return File(img_temp)
    except Exception as e:
        print(f"Error getting image from URL: {e}")
        return None

def create_sample_auction():
    # Get admin user
    try:
        seller = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("Admin user not found. Please create an admin user first.")
        return
    
    # Get a random category
    try:
        categories = Category.objects.all()
        if not categories.exists():
            print("No categories found. Please create categories first.")
            return
        
        category = random.choice(categories)
    except Exception as e:
        print(f"Error getting category: {e}")
        return
    
    # Sample auction data
    title = f"Sample {category.name} Auction"
    slug = slugify(title)
    
    # Check if this auction already exists
    if Auction.objects.filter(slug=slug).exists():
        print(f"Sample auction '{title}' already exists.")
        return
    
    # Create the auction
    try:
        end_date = timezone.now() + timedelta(days=7)
        starting_price = round(random.uniform(19.99, 999.99), 2)
        
        description = f"""
This is a sample auction for a {category.name} item.

Features:
- High quality product
- Great condition
- Fast shipping
- Satisfaction guaranteed

This item is perfect for collectors and enthusiasts. Don't miss this opportunity!
        """

        # Create the auction object without saving yet
        auction = Auction(
            title=title,
            slug=slug,
            seller=seller,
            category=category,
            description=description,
            starting_price=starting_price,
            current_price=starting_price,
            end_date=end_date,
            status='ACTIVE',
            featured=True,
        )
        
        # Get placeholder image URL based on category
        category_name = category.name.lower()
        image_url = PLACEHOLDER_IMAGES.get(category_name, PLACEHOLDER_IMAGES['default'])
        
        # Get image file from URL
        img_file = get_image_from_url(image_url)
        if img_file:
            # Set the image and save
            image_name = f"{slug}.png"
            auction.image.save(image_name, img_file, save=False)
        
        # Save the auction
        auction.save()
        
        print(f"Created sample auction: {title}")
        print(f"Category: {category.name}")
        print(f"Starting price: ${starting_price}")
        print(f"End date: {end_date}")
        
        return auction
    except Exception as e:
        print(f"Error creating sample auction: {e}")
        return None

if __name__ == "__main__":
    print("Creating a sample auction...")
    create_sample_auction()
    print("Done!") 
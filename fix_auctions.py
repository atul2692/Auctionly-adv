import os
import django
import random
from datetime import timedelta
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_site.settings')
django.setup()

from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from auctions.models import Category, Auction

User = get_user_model()

def ensure_media_dirs():
    """Ensure the necessary media directories exist"""
    media_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')
    auction_images_dir = os.path.join(media_root, 'auction_images')
    
    os.makedirs(media_root, exist_ok=True)
    os.makedirs(auction_images_dir, exist_ok=True)
    
    return auction_images_dir

def create_dummy_image(auction_images_dir, filename):
    """Create a dummy image file in the auction_images directory"""
    image_path = os.path.join(auction_images_dir, filename)
    
    # Create a simple colored square as dummy image
    try:
        from PIL import Image
        img = Image.new('RGB', (600, 400), color=(73, 109, 137))
        img.save(image_path)
        return image_path
    except ImportError:
        print("Pillow not installed. Can't create dummy image.")
        return None

def ensure_admin_exists():
    """Make sure admin user exists"""
    try:
        admin = User.objects.get(username='admin')
        return admin
    except User.DoesNotExist:
        print("Admin user doesn't exist. Creating one...")
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='Admin123!',
            user_type='SELLER'
        )
        return admin

def ensure_category_exists(name="Test Category", description="Test category description"):
    """Make sure at least one category exists"""
    slug = slugify(name)
    try:
        category = Category.objects.get(slug=slug)
        return category
    except Category.DoesNotExist:
        print(f"Creating category: {name}")
        return Category.objects.create(
            name=name,
            slug=slug,
            description=description
        )

def create_auction_with_local_image():
    """Create a sample auction with a local image"""
    # Ensure directories exist
    auction_images_dir = ensure_media_dirs()
    
    # Ensure admin exists
    admin = ensure_admin_exists()
    
    # Ensure category exists
    category = ensure_category_exists()
    
    # Sample auction data
    title = f"Test Auction {random.randint(1000, 9999)}"
    slug = slugify(title)
    
    # Create a dummy image
    image_filename = f"{slug}.png"
    image_path = create_dummy_image(auction_images_dir, image_filename)
    
    if not image_path:
        print("Failed to create image. Cannot create auction.")
        return None
    
    # Create the auction
    end_date = timezone.now() + timedelta(days=7)
    starting_price = 99.99
    
    try:
        auction = Auction.objects.create(
            title=title,
            slug=slug,
            seller=admin,
            category=category,
            description="This is a test auction with a local image",
            starting_price=starting_price,
            current_price=starting_price,
            end_date=end_date,
            status='ACTIVE',
            featured=True,
            image=f"auction_images/{image_filename}"
        )
        
        print(f"Created auction: {title}")
        print(f"Category: {category.name}")
        print(f"Starting price: ${starting_price}")
        print(f"End date: {end_date}")
        
        return auction
    except Exception as e:
        print(f"Error creating auction: {e}")
        return None

if __name__ == "__main__":
    print("Creating a test auction with local image...")
    auction = create_auction_with_local_image()
    if auction:
        print("Done!")
    else:
        print("Failed to create auction.") 
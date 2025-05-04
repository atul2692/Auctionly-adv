#!/usr/bin/env python
import os
import requests
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

# Create directory for category images if it doesn't exist
os.makedirs('static/images/categories', exist_ok=True)

# Define category image URLs
category_images = {
    'electronics': 'https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1000&auto=format&fit=crop',
    'collectibles': 'https://images.unsplash.com/photo-1459257831348-f0cdd359235f?q=80&w=1000&auto=format&fit=crop',
    'art': 'https://images.unsplash.com/photo-1531913764164-f85c52e6e654?q=80&w=1000&auto=format&fit=crop',
    'fashion': 'https://images.unsplash.com/photo-1445205170230-053b83016050?q=80&w=1000&auto=format&fit=crop',
    'home-garden': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?q=80&w=1000&auto=format&fit=crop',
    'sports': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?q=80&w=1000&auto=format&fit=crop',
    'vehicles': 'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?q=80&w=1000&auto=format&fit=crop',
    'books-media': 'https://images.unsplash.com/photo-1524578271613-d550eacf6090?q=80&w=1000&auto=format&fit=crop',
    'toys-games': 'https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?q=80&w=1000&auto=format&fit=crop',
    'jewelry': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?q=80&w=1000&auto=format&fit=crop',
}

def download_and_optimize_image(url, save_path, width=800, height=400):
    """
    Download an image from URL, resize and optimize it, and save to the specified path
    """
    try:
        # Download image
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad responses
        
        # Open image from bytes
        img = Image.open(BytesIO(response.content))
        
        # Resize image while maintaining aspect ratio
        img.thumbnail((width, height), Image.LANCZOS)
        
        # Crop to exact dimensions if needed
        if img.width != width or img.height != height:
            # Create new image with desired dimensions
            new_img = Image.new('RGB', (width, height))
            
            # Calculate position to paste resized image centered
            paste_x = (width - img.width) // 2
            paste_y = (height - img.height) // 2
            
            # Paste resized image onto new canvas
            new_img.paste(img, (paste_x, paste_y))
            img = new_img
        
        # Save optimized image
        img.save(save_path, optimize=True, quality=85)
        print(f"Downloaded and saved: {save_path}")
        return True
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return False

# Download each category image
for category, url in category_images.items():
    file_path = f'static/images/categories/{category}.jpg'
    download_and_optimize_image(url, file_path)

print("Category image download complete!") 
#!/usr/bin/env python
import os
import requests
from PIL import Image
from io import BytesIO

# URL for a good abstract art image that matches the one in the chat
HERO_IMAGE_URL = "https://images.unsplash.com/photo-1676425074042-f39c917ec0cc?q=80&w=1600&auto=format&fit=crop"

def download_and_save_image(url, save_path, width=1600):
    """Download an image from URL and save it to the specified path"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Download image
        response = requests.get(url)
        response.raise_for_status()
        
        # Open and process image
        img = Image.open(BytesIO(response.content))
        
        # Resize while maintaining aspect ratio
        aspect_ratio = img.height / img.width
        new_height = int(width * aspect_ratio)
        img = img.resize((width, new_height), Image.LANCZOS)
        
        # Save image
        img.save(save_path, quality=90, optimize=True)
        print(f"Abstract hero image downloaded and saved to {save_path}")
        return True
    except Exception as e:
        print(f"Error downloading abstract hero image: {e}")
        return False

if __name__ == "__main__":
    # Save hero image
    download_and_save_image(HERO_IMAGE_URL, "static/images/abstract-art-hero.jpg") 
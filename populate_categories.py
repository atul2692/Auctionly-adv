#!/usr/bin/env python
"""
Populate the database with initial categories for the auction site.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_site.settings')
django.setup()

from auctions.models import Category
from django.utils.text import slugify

# List of common auction categories
CATEGORIES = [
    {
        "name": "Electronics",
        "description": "Computers, smartphones, tablets, and other electronic devices."
    },
    {
        "name": "Collectibles",
        "description": "Rare items, antiques, coins, stamps, and other collectibles."
    },
    {
        "name": "Art",
        "description": "Paintings, sculptures, prints, and other artwork."
    },
    {
        "name": "Jewelry",
        "description": "Fine jewelry, watches, and accessories."
    },
    {
        "name": "Fashion",
        "description": "Clothing, shoes, bags, and other fashion items."
    },
    {
        "name": "Home & Garden",
        "description": "Furniture, home decor, gardening tools, and other household items."
    },
    {
        "name": "Sports",
        "description": "Sports equipment, memorabilia, and other sporting goods."
    },
    {
        "name": "Vehicles",
        "description": "Cars, motorcycles, boats, and other vehicles."
    },
    {
        "name": "Books & Media",
        "description": "Books, movies, music, and other media."
    },
    {
        "name": "Toys & Games",
        "description": "Toys, board games, video games, and other entertainment items."
    },
]

def create_categories():
    """Create categories if they don't exist"""
    print("Creating categories...")
    
    for category_data in CATEGORIES:
        name = category_data["name"]
        description = category_data["description"]
        slug = slugify(name)
        
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={
                "slug": slug,
                "description": description
            }
        )
        
        if created:
            print(f"Created category: {name}")
        else:
            print(f"Category already exists: {name}")
    
    print(f"Total categories: {Category.objects.count()}")

if __name__ == "__main__":
    create_categories() 
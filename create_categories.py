import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_site.settings')
django.setup()

from django.utils.text import slugify
from auctions.models import Category

# Define the categories to create
categories = [
    {
        'name': 'Electronics',
        'description': 'Computers, phones, and other electronic devices'
    },
    {
        'name': 'Collectibles',
        'description': 'Rare items, memorabilia, and collectible treasures'
    },
    {
        'name': 'Fashion',
        'description': 'Clothing, accessories, and footwear'
    },
    {
        'name': 'Home & Garden',
        'description': 'Furniture, appliances, and gardening tools'
    },
    {
        'name': 'Art',
        'description': 'Paintings, sculptures, and other art pieces'
    },
    {
        'name': 'Vehicles',
        'description': 'Cars, motorcycles, and other vehicles'
    },
    {
        'name': 'Jewelry',
        'description': 'Rings, necklaces, watches, and other jewelry items'
    },
    {
        'name': 'Sports',
        'description': 'Sports equipment, memorabilia, and fitness gear'
    },
]

# Create the categories
created_count = 0
for category_data in categories:
    try:
        # Check if the category already exists
        slug = slugify(category_data['name'])
        if not Category.objects.filter(slug=slug).exists():
            Category.objects.create(
                name=category_data['name'],
                slug=slug,
                description=category_data['description']
            )
            created_count += 1
            print(f"Created category: {category_data['name']}")
        else:
            print(f"Category already exists: {category_data['name']}")
    except Exception as e:
        print(f"Error creating category {category_data['name']}: {e}")

print(f"\nSuccessfully created {created_count} categories!") 
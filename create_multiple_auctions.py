import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_site.settings')
django.setup()

from create_sample_auction import create_sample_auction

# Create multiple sample auctions
def create_multiple_auctions(count=5):
    print(f"Creating {count} sample auctions...")
    
    successful = 0
    for i in range(count):
        auction = create_sample_auction()
        if auction:
            successful += 1
    
    print(f"Successfully created {successful} out of {count} auctions.")

if __name__ == "__main__":
    create_multiple_auctions(10) 
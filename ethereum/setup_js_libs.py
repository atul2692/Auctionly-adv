#!/usr/bin/env python
"""
Setup script for downloading JavaScript libraries needed for Ethereum integration.
This script will download ethers.js and save it to the static directory.
"""

import os
import sys
import requests
from pathlib import Path

def print_header(message):
    """Print a header message."""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80)

def print_step(message):
    """Print a step message."""
    print(f"\n>> {message}")

def setup_static_dir():
    """Create static/js directory if it doesn't exist."""
    print_step("Setting up static directory...")
    
    # Get base directory
    base_dir = Path(__file__).resolve().parent.parent
    
    # Create static/js directory if it doesn't exist
    js_dir = base_dir / 'static' / 'js'
    js_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Created directory: {js_dir}")
    return js_dir

def download_ethers_js(js_dir):
    """Download ethers.js library."""
    print_step("Downloading ethers.js...")
    
    ethers_url = "https://cdn.ethers.io/lib/ethers-5.2.umd.min.js"
    output_path = js_dir / 'ethers.min.js'
    
    try:
        response = requests.get(ethers_url)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded ethers.js to {output_path}")
        return True
    except Exception as e:
        print(f"Error downloading ethers.js: {e}")
        print("\nAlternative: You can manually download ethers.js from https://cdn.ethers.io/lib/ethers-5.2.umd.min.js")
        print(f"and save it to {output_path}")
        return False

def update_base_template():
    """Provide instructions for updating the base template."""
    print_step("Updating base template...")
    
    base_dir = Path(__file__).resolve().parent.parent
    template_path = base_dir / 'templates' / 'base.html'
    
    if not template_path.exists():
        print(f"Base template not found at {template_path}")
        print("You'll need to manually update your base template")
    
    print("\nAdd the following line to your base.html template in the head section:")
    print('<script src="{% static \'js/ethers.min.js\' %}"></script>')
    
    print("\nMake sure to include the static tag at the top of your template:")
    print('{% load static %}')

def main():
    """Main function."""
    print_header("AuctionHub - JavaScript Libraries Setup")
    
    print("""
This script will download the ethers.js library needed for Ethereum integration.
    """)
    
    js_dir = setup_static_dir()
    download_success = download_ethers_js(js_dir)
    
    if download_success:
        update_base_template()
        
        print_header("Setup completed successfully!")
        print("""
Next steps:
1. Update your base template to include the ethers.js library
2. Make sure your Django static files are properly configured
3. Run collectstatic if needed: python manage.py collectstatic
        """)
    else:
        print_header("Setup failed. Please fix the issues and try again.")

if __name__ == "__main__":
    main() 
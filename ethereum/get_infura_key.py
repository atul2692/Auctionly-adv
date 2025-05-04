#!/usr/bin/env python
"""
Helper script to get and configure an Infura API key for Ethereum integration.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(message):
    """Print a header message."""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80)

def print_step(message):
    """Print a step message."""
    print(f"\n>> {message}")

def main():
    """Main function to guide user through Infura setup."""
    print_header("Ethereum Integration - Infura API Key Setup")
    
    print("""
To connect to Ethereum networks like Sepolia testnet, you need an Infura API key.
Follow these steps to get a free API key and configure your project:

1. Go to https://app.infura.io/register to create a free Infura account
2. After registering and logging in, create a new API key:
   - Click "Create New API Key"
   - Select "Web3 API" as the network
   - Give your project a name (e.g., "AuctionHubDev")
   - Select the networks you need (at minimum, select "Sepolia")
3. Once created, copy the "API KEY" value (not the secret)
    """)
    
    infura_key = input("\nEnter your Infura API KEY: ").strip()
    
    if not infura_key:
        print("Error: API key cannot be empty")
        return
    
    # Find the Django settings file
    settings_path = Path(__file__).resolve().parent.parent / "auction_site" / "settings.py"
    
    if not settings_path.exists():
        print(f"Error: Could not find settings file at {settings_path}")
        return
    
    print_step("Updating settings.py with your Infura API key...")
    
    # Read the settings file
    with open(settings_path, 'r') as f:
        settings_content = f.read()
    
    # Replace the placeholder with the actual API key
    if "YOUR_INFURA_PROJECT_ID" in settings_content:
        updated_content = settings_content.replace("YOUR_INFURA_PROJECT_ID", infura_key)
        
        # Write the updated content back to the file
        with open(settings_path, 'w') as f:
            f.write(updated_content)
        
        print("Settings updated successfully!")
    else:
        print("Could not find the placeholder in settings.py. You may need to manually update the file.")
        print(f"Please open {settings_path} and replace YOUR_INFURA_PROJECT_ID with {infura_key}")
    
    print_header("Setup completed!")
    print("""
Next steps:
1. Make sure you have deployed your contracts to Sepolia testnet
2. Update AUCTION_CONTRACT_ADDRESS in settings.py with your deployed contract address
3. Run your Django server and test the integration
    """)

if __name__ == "__main__":
    main() 
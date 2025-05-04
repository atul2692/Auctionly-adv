#!/usr/bin/env python
"""
Setup script for the Ethereum integration.
This script will guide you through the process of setting up the Ethereum integration.
"""

import os
import sys
import shutil
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

def check_requirements():
    """Check if the required dependencies are installed."""
    print_step("Checking requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        return False
    
    # Check Node.js
    try:
        subprocess.run(["node", "--version"], check=True, stdout=subprocess.PIPE)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: Node.js is required but not found.")
        print("Please install Node.js from https://nodejs.org/")
        return False
    
    # Check npm
    try:
        subprocess.run(["npm", "--version"], check=True, stdout=subprocess.PIPE)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: npm is required but not found.")
        print("Please install npm (it usually comes with Node.js)")
        return False
    
    return True

def setup_npm_packages():
    """Install npm packages."""
    print_step("Installing npm packages...")
    
    os.chdir("ethereum")
    subprocess.run(["npm", "install"], check=True)
    os.chdir("..")
    
    print("npm packages installed successfully.")

def install_hardhat():
    """Install Hardhat globally."""
    print_step("Installing Hardhat...")
    
    try:
        subprocess.run(["npx", "hardhat", "--version"], check=True, stdout=subprocess.PIPE)
        print("Hardhat is already installed.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Installing Hardhat...")
        subprocess.run(["npm", "install", "--global", "hardhat"], check=True)
        print("Hardhat installed successfully.")

def install_ganache():
    """Provide instructions for installing Ganache."""
    print_step("Installing Ganache...")
    
    print("Ganache is a personal Ethereum blockchain for local development and testing.")
    print("Please download and install Ganache from https://trufflesuite.com/ganache/")
    print("After installation, create a new workspace with the following settings:")
    print("1. RPC Server: http://127.0.0.1:8545")
    print("2. Network ID: 1337")
    
    input("Press Enter when you have installed Ganache and it's running...")

def compile_contracts():
    """Compile the Ethereum contracts."""
    print_step("Compiling contracts...")
    
    os.chdir("ethereum")
    result = subprocess.run(["npx", "hardhat", "compile"], check=True)
    os.chdir("..")
    
    if result.returncode == 0:
        print("Contracts compiled successfully.")
    else:
        print("Error compiling contracts.")

def setup_environment_vars():
    """Setup environment variables."""
    print_step("Setting up environment variables...")
    
    print("After deploying the contracts, you will need to set the following environment variables:")
    print("export AUCTION_CONTRACT_ADDRESS='0x...'")
    print("export PAYMENT_PROCESSOR_ADDRESS='0x...'")
    print("export ETH_PRIVATE_KEY='0x...'")
    
    print("\nYou can get these values after deploying the contracts with:")
    print("cd ethereum && npx hardhat run scripts/deploy.js --network ganache")

def main():
    """Main function."""
    print_header("AuctionHub - Ethereum Integration Setup")
    
    print("""
This script will guide you through the process of setting up the Ethereum integration
for the AuctionHub project. It will check requirements, install dependencies, and
help you configure the environment.
    """)
    
    if not check_requirements():
        print_header("Setup failed. Please fix the issues and try again.")
        return
    
    setup_npm_packages()
    install_hardhat()
    install_ganache()
    compile_contracts()
    setup_environment_vars()
    
    print_header("Setup completed successfully!")
    print("""
Next steps:
1. Start Ganache and keep it running
2. Deploy the contracts: cd ethereum && npx hardhat run scripts/deploy.js --network ganache
3. Set the environment variables with the contract addresses
4. Start the Django server: python manage.py runserver
    """)

if __name__ == "__main__":
    main() 
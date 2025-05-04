#!/usr/bin/env python
"""
Installation script for Ethereum dependencies.
"""

import os
import sys
import subprocess
import platform

def print_header(message):
    """Print a header message."""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80)

def print_step(message):
    """Print a step message."""
    print(f"\n>> {message}")

def install_dependencies():
    """Install required dependencies."""
    print_step("Installing required Ethereum dependencies...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're in a virtual environment
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("WARNING: You are not in a virtual environment. It's recommended to use a virtual environment.")
        response = input("Continue with installation? (y/n): ")
        if response.lower() != 'y':
            print("Installation aborted.")
            return False
    
    # Get the requirements file path
    requirements_path = os.path.join(script_dir, "requirements.txt")
    
    if not os.path.exists(requirements_path):
        print(f"Error: Could not find requirements.txt at {requirements_path}")
        return False
    
    # Install dependencies using pip
    try:
        print("\nInstalling packages with pip. This may take a few minutes...")
        
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        
        print("\n✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing dependencies: {e}")
        return False

def main():
    """Main function."""
    print_header("Ethereum Integration - Dependencies Installation")
    
    if platform.system() == 'Windows':
        print("Running on Windows")
    elif platform.system() == 'Linux':
        print("Running on Linux")
    elif platform.system() == 'Darwin':
        print("Running on macOS")
    
    if install_dependencies():
        print_header("Installation Completed Successfully!")
        print("\nYou can now run the test connection script:")
        print("python test_connection.py")
    else:
        print_header("Installation Failed")
        print("\nPlease try to manually install the dependencies:")
        print("pip install web3 django ethtoken python-dotenv")

if __name__ == "__main__":
    main() 
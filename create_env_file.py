#!/usr/bin/env python
"""
This script creates a .env file from .env.example template.
It prompts the user for values or uses defaults where appropriate.
"""

import os
import secrets
import sys

def generate_secret_key():
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(50)

def main():
    print("Creating .env file from template...")
    
    # Check if .env file already exists
    if os.path.exists('.env'):
        overwrite = input("A .env file already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("Aborting.")
            return
    
    # Check if .env.example exists
    if not os.path.exists('.env.example'):
        print("Creating a new .env file from scratch...")
        template_lines = []
    else:
        # Read the example file
        with open('.env.example', 'r') as f:
            template_lines = f.readlines()
    
    env_vars = {}
    
    # Process template lines
    for line in template_lines:
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        if '=' in line:
            key, default_value = line.split('=', 1)
            
            # Automatically generate a secret key if needed
            if key == 'DJANGO_SECRET_KEY' and (not default_value or default_value == 'your-secret-key-here'):
                value = generate_secret_key()
                print(f"Generated a new secret key.")
            else:
                # Prompt for other values
                value = input(f"Enter value for {key} (default: '{default_value}'): ")
                if not value:
                    value = default_value
            
            env_vars[key] = value
    
    # Check for important keys that might be missing
    required_keys = [
        ('DJANGO_SECRET_KEY', generate_secret_key()),
        ('DJANGO_DEBUG', 'True'),
        ('ALLOWED_HOSTS', 'localhost,127.0.0.1'),
        ('EMAIL_HOST_USER', ''),
        ('EMAIL_HOST_PASSWORD', ''),
        ('RAZORPAY_KEY_ID', ''),
        ('RAZORPAY_KEY_SECRET', '')
    ]
    
    for key, default in required_keys:
        if key not in env_vars:
            if key == 'DJANGO_SECRET_KEY':
                value = default
                print(f"Generated a new secret key.")
            else:
                value = input(f"Enter value for {key} (default: '{default}'): ")
                if not value:
                    value = default
            env_vars[key] = value
    
    # Write the .env file
    with open('.env', 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print("\n.env file created successfully!")
    print("Remember to keep this file private and never commit it to version control.")

if __name__ == "__main__":
    main() 
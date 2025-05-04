#!/usr/bin/env python
"""
Setup script for AuctionHub project.
This script automates the initial setup process.
"""

import os
import subprocess
import sys
import platform

def run_command(command, shell=True):
    """Run a shell command and print output."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=shell, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Command failed with error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def create_venv():
    """Create a virtual environment."""
    if os.path.exists('env'):
        print("Virtual environment already exists.")
        return True
    
    print("Creating virtual environment...")
    return run_command(f"{sys.executable} -m venv env")

def activate_venv():
    """Return the activation command for the virtual environment."""
    if platform.system() == "Windows":
        return ".\\env\\Scripts\\activate"
    else:
        return "source env/bin/activate"

def install_requirements():
    """Install Python dependencies."""
    print("Installing requirements...")
    pip_path = os.path.join('env', 'Scripts' if platform.system() == 'Windows' else 'bin', 'pip')
    return run_command(f"{pip_path} install -r requirements.txt")

def setup_env_file():
    """Set up the environment variables file."""
    if not os.path.exists('.env.example'):
        print("ERROR: .env.example file not found!")
        return False
    
    if not os.path.exists('.env'):
        print("Setting up .env file...")
        if os.path.exists('create_env_file.py'):
            return run_command(f"{sys.executable} create_env_file.py")
        else:
            print("Copying .env.example to .env")
            with open('.env.example', 'r') as src, open('.env', 'w') as dest:
                dest.write(src.read())
    else:
        print(".env file already exists.")
    
    return True

def run_migrations():
    """Run Django migrations."""
    print("Running migrations...")
    return run_command(f"{sys.executable} manage.py migrate")

def create_superuser():
    """Create a Django superuser if needed."""
    response = input("Do you want to create a superuser? (y/n): ")
    if response.lower() == 'y':
        return run_command(f"{sys.executable} manage.py createsuperuser")
    return True

def main():
    """Main setup function."""
    print("Starting AuctionHub setup...")
    
    steps = [
        ("Creating virtual environment", create_venv),
        ("Setting up environment variables", setup_env_file),
        ("Installing requirements", install_requirements),
        ("Running migrations", run_migrations),
        ("Creating superuser", create_superuser)
    ]
    
    for step_name, step_func in steps:
        print(f"\n--- {step_name} ---")
        if not step_func():
            print(f"ERROR: Failed at step: {step_name}")
            return
    
    print("\nSetup completed successfully!")
    print(f"\nTo activate the virtual environment, run:\n{activate_venv()}")
    print("\nTo start the development server:")
    print("1. Activate the virtual environment")
    print("2. Run: python manage.py runserver")
    
    if platform.system() == "Windows":
        print("\nTo start Redis and Celery:")
        print("1. Run: .\\start_redis.bat")
        print("2. Run: .\\start_celery.bat")
    else:
        print("\nTo start Redis and Celery:")
        print("1. Start Redis server")
        print("2. Run: celery -A auction_site worker -l info")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python
"""
Simple script to run database migrations for the auction project.
This can be run manually if migrations are needed.
"""

import os
import subprocess
import sys

def main():
    print("Running migrations for AuctionHub project...")
    try:
        result = subprocess.run(
            [sys.executable, "manage.py", "migrate"],
            check=True,
            text=True,
            capture_output=True
        )
        print(result.stdout)
        print("Migrations completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        print(e.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
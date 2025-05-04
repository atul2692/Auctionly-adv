#!/usr/bin/env python
"""
This script creates a .env.example file with template values.
"""

ENV_EXAMPLE_CONTENT = """# Django settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email settings
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-email@example.com

# Celery settings
CELERY_BROKER_URL=redis://localhost:6379/0

# Ethereum settings
DEFAULT_ETH_ADDRESS=0x1234567890123456789012345678901234567890
ETH_NETWORK_URL=https://sepolia.infura.io/v3/YOUR_INFURA_API_KEY
ETH_CHAIN_ID=11155111
AUCTION_CONTRACT_ADDRESS=your-contract-address-here
PAYMENT_PROCESSOR_ADDRESS=your-payment-processor-address-here

# Razorpay settings
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-secret-key
"""

def main():
    with open('.env.example', 'w') as f:
        f.write(ENV_EXAMPLE_CONTENT)
    print('.env.example file created successfully!')

if __name__ == "__main__":
    main() 
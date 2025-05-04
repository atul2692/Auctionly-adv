#!/bin/bash
# Setup script for Ethereum deployment

echo "==================================================="
echo "  Ethereum Deployment Setup"
echo "==================================================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python is required but not found. Please install Python first."
    exit 1
fi

# Create .env file for deployment
cat > .env << EOL
# Ethereum Deployment Configuration
# Generated on $(date)

# Infura API settings
INFURA_PROJECT_ID=your_infura_project_id
INFURA_SEPOLIA_URL=https://sepolia.infura.io/v3/your_infura_project_id

# Ethereum wallet settings
# WARNING: Never commit this file to version control!
PRIVATE_KEY=your_ethereum_private_key
EOL

echo "Created .env file template at ethereum/.env"
echo ""
echo "Next steps:"
echo "1. Get your Infura API key by running: python get_infura_key.py"
echo "2. Edit the .env file with your Ethereum private key"
echo "3. Run deployment with: source .env && npx hardhat run scripts/deploy-sepolia.js --network sepolia"
echo ""
echo "IMPORTANT SECURITY WARNING: Keep your private key secret!"
echo "Never commit the .env file to version control or share it with others."
echo ""

# Ask if the user wants to run the Infura setup script
read -p "Would you like to run the Infura setup script now? (y/n): " run_infura

if [ "$run_infura" = "y" ] || [ "$run_infura" = "Y" ]; then
    python get_infura_key.py
fi

echo ""
echo "Setup complete!" 
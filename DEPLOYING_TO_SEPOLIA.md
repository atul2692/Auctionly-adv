# Deploying Smart Contracts to Sepolia Testnet

This guide will walk you through the process of deploying your smart contracts to the Ethereum Sepolia testnet.

## Prerequisites

Before you begin, ensure you have:

1. **Node.js and npm installed** - You already have Node.js v22.13.1 and npm v10.9.2
2. **An Ethereum wallet with private key** - You need a wallet and its private key for deployment
3. **Sepolia testnet ETH** - You need some test ETH for gas fees
4. **Infura API key** - You already have this: c592d537c4514e66b9af8b15770bc347

## Step 1: Prepare Your Private Key

1. **Get your Ethereum wallet's private key**:
   - If using MetaMask: Open MetaMask → Click on the three dots → Account Details → Export Private Key
   - **IMPORTANT**: Keep your private key secure! Never share it or commit it to version control

2. **Edit the deployment variables script**:
   - Open `ethereum/set_deploy_vars.ps1` in a text editor
   - Replace the `YOUR_PRIVATE_KEY` placeholder with your actual private key:
   
   ```powershell
   $privateKey = "123abc..." # Your actual private key here
   ```
   
   - Save the file

## Step 2: Get Sepolia Testnet ETH

You need Sepolia ETH to pay for gas fees when deploying contracts.

1. **Get Sepolia testnet ETH from a faucet**:
   - Visit [Sepolia Faucet](https://sepoliafaucet.com/) or [Sepolia Faucet (Alternative)](https://sepolia-faucet.pk910.de/)
   - Enter your wallet address
   - Complete any verification steps
   - Wait for the test ETH to be sent to your wallet

## Step 3: Set Up Environment Variables

1. **Run the environment variables script**:
   ```powershell
   .\ethereum\set_deploy_vars.ps1
   ```
   
   This will set the necessary environment variables for deployment.
   
   Make sure you see the confirmation that your environment variables are set correctly.

## Step 4: Deploy Your Contracts

1. **Navigate to the ethereum directory**:
   ```powershell
   cd ethereum
   ```

2. **Run the deployment script**:
   ```powershell
   npx hardhat run scripts/deploy-sepolia.js --network sepolia
   ```

3. **Wait for deployment to complete**:
   - The deployment process may take a minute or two
   - You'll see the contract addresses printed in the console when deployment is successful
   - The script will also save the deployment information to `ethereum/deployment-sepolia.json`

## Step 5: Update Your Django Settings

1. **Open your Django settings file** (`auction_site/settings.py`)

2. **Update the `AUCTION_CONTRACT_ADDRESS` setting**:
   ```python
   AUCTION_CONTRACT_ADDRESS = "0x..." # Replace with your deployed contract address
   ```

## Step 6: Verify Your Deployment

1. **Check your contract on Sepolia Etherscan**:
   - Visit [Sepolia Etherscan](https://sepolia.etherscan.io/)
   - Paste your contract address in the search bar
   - Verify that your contract is deployed

2. **Test the contract connection**:
   - Run the test script:
   ```powershell
   python test_direct_connection.py
   ```
   
   - If everything is working correctly, you should see "Successfully connected to Ethereum node!"

## Troubleshooting

If you encounter any issues during deployment:

1. **Insufficient funds error**:
   - Make sure you have enough Sepolia ETH for gas fees
   - Get more from a Sepolia faucet

2. **Contract deployment failures**:
   - Check your private key is correct
   - Ensure your Infura API key is valid
   - Check that your contract compiles correctly

3. **Connection issues**:
   - Verify your Infura API key is correct
   - Make sure your Infura project has access to the Sepolia network

4. **Configuration errors**:
   - Double-check your hardhat.config.js settings
   - Ensure environment variables are set correctly

## Security Notes

- **NEVER share your private key** with anyone
- **NEVER commit your private key** to version control
- Consider using environment variables or a .env file (with proper .gitignore) instead of hardcoding sensitive information
- For production deployments, use a more secure approach for managing private keys 
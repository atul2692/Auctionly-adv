# PowerShell script to set environment variables for Ethereum deployment
# Run this script before deploying contracts

# Set Infura API settings
$env:INFURA_PROJECT_ID = "YOUR_INFURA_PROJECT_ID"
$env:INFURA_SEPOLIA_URL = "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"

# Set Ethereum wallet settings
$env:PRIVATE_KEY = "YOUR_ETHEREUM_PRIVATE_KEY"

# Confirm environment variables are set
Write-Host "Environment variables have been set for Ethereum deployment:"
Write-Host "INFURA_PROJECT_ID: $env:INFURA_PROJECT_ID"
Write-Host "INFURA_SEPOLIA_URL: $env:INFURA_SEPOLIA_URL"
Write-Host "PRIVATE_KEY: " $env:PRIVATE_KEY.Substring(0, 4) + "..." + $env:PRIVATE_KEY.Substring($env:PRIVATE_KEY.Length - 4)
Write-Host ""
Write-Host "You can now deploy your contracts with the following command:"
Write-Host "npx hardhat run scripts/deploy-sepolia.js --network sepolia" 
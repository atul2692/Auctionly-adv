# PowerShell script to set environment variables for Ethereum deployment
# Run this script before deploying contracts

# Please replace the placeholders below with your actual keys
$infuraProjectId = "c592d537c4514e66b9af8b15770bc347"  # Your Infura project ID - already set in settings.py
# IMPORTANT: Replace the line below with your actual private key when running this script
$privateKey = "fd908dcd17fd29b2de68aeadcc643e3aa026109b9515cfc801f731afc42be37f" # Replace with your actual private key when ready to deploy

# Set Infura API settings
$env:INFURA_PROJECT_ID = $infuraProjectId
$env:INFURA_SEPOLIA_URL = "https://sepolia.infura.io/v3/$infuraProjectId"

# Set Ethereum wallet settings
$env:PRIVATE_KEY = $privateKey

# Safety check for private key placeholder
if ($env:PRIVATE_KEY -eq "YOUR_PRIVATE_KEY") {
    Write-Host "ERROR: You must edit this script and replace 'YOUR_PRIVATE_KEY' with your actual private key." -ForegroundColor Red
    Write-Host "NEVER commit your private key to version control or share it with anyone!" -ForegroundColor Red
    exit 1
}

# Confirm environment variables are set
Write-Host "Environment variables have been set for Ethereum deployment:" -ForegroundColor Green
Write-Host "INFURA_PROJECT_ID: $env:INFURA_PROJECT_ID" -ForegroundColor Green
Write-Host "INFURA_SEPOLIA_URL: $env:INFURA_SEPOLIA_URL" -ForegroundColor Green
# Only show first and last 4 characters of the private key for security
if ($env:PRIVATE_KEY.Length -gt 8) {
    $maskedKey = $env:PRIVATE_KEY.Substring(0, 4) + "..." + $env:PRIVATE_KEY.Substring($env:PRIVATE_KEY.Length - 4)
    Write-Host "PRIVATE_KEY: $maskedKey" -ForegroundColor Green
}

Write-Host ""
Write-Host "Checking for Sepolia ETH balance..." -ForegroundColor Yellow
Write-Host "Make sure you have enough Sepolia ETH for the deployment." -ForegroundColor Yellow
Write-Host "If you need Sepolia ETH, visit https://sepoliafaucet.com/ or https://sepolia-faucet.pk910.de/" -ForegroundColor Yellow

Write-Host ""
Write-Host "You can now deploy your contracts with the following command:" -ForegroundColor Cyan
Write-Host "npx hardhat run scripts/deploy-sepolia.js --network sepolia" -ForegroundColor Cyan 
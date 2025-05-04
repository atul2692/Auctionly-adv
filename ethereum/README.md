# Ethereum Integration

This module adds Ethereum blockchain integration to the AuctionHub platform, allowing for:

1. Smart contract-based auctions on Ethereum
2. USD to ETH conversion for payments
3. Payment verification and processing

## Setup Instructions

### 1. Install Required Dependencies

```bash
pip install web3 eth-utils
```

### 2. Install and Run Ganache

Ganache is a personal Ethereum blockchain for local development and testing.

1. Download and install Ganache from https://trufflesuite.com/ganache/
2. Launch Ganache and create a new workspace
3. Make sure it's running on http://127.0.0.1:8545

### 3. Deploy Smart Contracts

```bash
# Install Hardhat (requires Node.js)
npm install -g hardhat

# Install dependencies 
cd ethereum
npm install

# Compile and deploy contracts
npx hardhat compile
npx hardhat run scripts/deploy.js --network ganache
```

### 4. Configure Contract Addresses

After deploying the contracts, set the following environment variables with the deployed addresses:

```
export AUCTION_CONTRACT_ADDRESS="0x..."
export PAYMENT_PROCESSOR_ADDRESS="0x..."
export ETH_PRIVATE_KEY="0x..." # Private key for the first Ganache account
```

## Smart Contracts

1. **AuctionContract.sol**: Manages the Ethereum auctions
2. **PriceConverter.sol**: Handles USD to ETH conversion
3. **PaymentProcessor.sol**: Processes payments for auctions

## Integration Flow

1. User wins an auction in the Django app
2. User clicks "Pay with Ethereum" button
3. System converts USD price to ETH at current market rate
4. User completes payment using MetaMask or manual transaction
5. Payment is verified and recorded in both the blockchain and Django database 
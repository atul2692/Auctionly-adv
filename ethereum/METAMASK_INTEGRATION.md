# MetaMask Integration Guide

This guide explains how the AuctionHub platform integrates with MetaMask to enable Ethereum bidding.

## Setup Requirements

1. **ethers.js**: JavaScript library for interacting with Ethereum
2. **MetaMask**: Browser extension wallet

## Setup Instructions

1. Run the JavaScript library setup script:
   ```bash
   python ethereum/setup_js_libs.py
   ```

2. Add ethers.js to your base template:
   ```html
   {% load static %}
   <!-- In the head section -->
   <script src="{% static 'js/ethers.min.js' %}"></script>
   ```

3. Update your settings.py with the correct contract address:
   ```python
   AUCTION_CONTRACT_ADDRESS = "0x..." # Your deployed contract address
   ```

## How It Works

### 1. Detecting MetaMask

The code checks if MetaMask is installed in the user's browser:

```javascript
if (typeof window.ethereum !== 'undefined') {
    // MetaMask is installed
    // Setup ethers provider
    provider = new ethers.providers.Web3Provider(window.ethereum);
} else {
    // MetaMask is not installed
    // Show installation instructions
}
```

### 2. Connecting to MetaMask

When the user clicks "Connect Wallet", we request account access:

```javascript
async function connectWallet() {
    // Request account access
    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
    handleAccountsChanged(accounts);
    
    // Setup signer and contract
    signer = provider.getSigner();
    auctionContract = new ethers.Contract(contractAddress, auctionContractABI, signer);
}
```

### 3. Placing Bids with MetaMask

When placing a bid, we:
1. Convert the ETH amount to wei
2. Create a transaction to call the contract's `placeBid` function
3. Wait for the transaction to be confirmed
4. Show the result to the user

```javascript
// Call the placeBid function on the contract
const tx = await auctionContract.placeBid(auctionId, {
    value: bidAmountWei
});

// Wait for transaction to be mined
const receipt = await tx.wait();
```

### 4. Real-time Updates

The system periodically checks for updates:
1. Fetches the current highest bid from the smart contract
2. Updates the UI with the latest information
3. Notifies the user if they've been outbid

## Error Handling

The integration includes handling for common errors:
- User rejecting the transaction
- MetaMask not installed
- Smart contract errors
- Network issues

## Testing

To test the integration:
1. Install MetaMask in your browser
2. Connect to the local Ganache network (RPC URL: http://127.0.0.1:8545, Chain ID: 1337)
3. Import a test account from Ganache using its private key
4. Place bids using the MetaMask interface 
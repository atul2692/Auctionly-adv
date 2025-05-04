# Ethereum Integration Setup

This guide will help you set up the Ethereum blockchain integration for the auction platform.

## Connection Error Troubleshooting

If you're encountering a connection error similar to:
```
ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8545): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001F738156A70>': Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
```

This means your application is trying to connect to a local Ethereum node (Ganache) at `127.0.0.1:8545`, but the connection is being refused because there's no Ethereum node running at that address.

## Required Dependencies

Before you can use the Ethereum integration, you need to install the required Python packages:

```bash
# Install the required packages
pip install web3 django ethtoken

# For development, you may also want to install
pip install pytest-django eth-brownie eth-tester
```

## Solution: Use Infura Instead of Local Node

We've updated the system to use Infura's Ethereum Sepolia testnet instead of requiring a local Ethereum node.

### Step 1: Get an Infura API Key

1. Run the helper script to set up your Infura API key:

```bash
python ethereum/get_infura_key.py
```

2. Follow the instructions in the script to create an Infura account and get your API key.

### Step 2: Deploy Your Auction Contract

If you haven't already deployed your auction contract to the Sepolia testnet:

1. Get some test ETH from a Sepolia faucet:
   - Visit https://sepoliafaucet.com/ or https://sepolia-faucet.pk910.de/
   
2. Deploy your contract using Hardhat:
   ```bash
   cd ethereum
   npx hardhat run scripts/deploy.js --network sepolia
   ```

3. Update the `AUCTION_CONTRACT_ADDRESS` in your `settings.py` with the deployed contract address.

### Step 3: Test the Connection

1. Run the test connection script:
   ```bash
   python test_connection.py
   ```

2. If everything is working correctly, you should see "Successfully connected to Ethereum node!"

3. Start your Django server:
   ```bash
   python manage.py runserver
   ```

## Testing the Event Listener

Once your connection is working, you can test the event listener:

```bash
python manage.py shell
```

```python
from ethereum.event_listener import EventListener
listener = EventListener()
listener.run(run_once=True)  # Run once to test
```

## Troubleshooting

### Connection Issues
If you still have connection issues:

1. Check your Infura API key is correct in `settings.py`
2. Make sure you've selected Sepolia network in your Infura project settings
3. Verify your internet connection

### "No module named 'web3'" Error
If you see this error, install the required dependencies:

```bash
pip install web3 django ethtoken
```

### Contract Interaction Issues
If you can connect but have issues with contract interactions:

1. Verify your contract address is correct in `settings.py`
2. Check that your contract is deployed on the Sepolia testnet
3. Make sure your contract ABI matches the deployed contract

## Local Development Option

If you prefer to use a local Ethereum node (like Ganache) for development:

1. Install and run Ganache:
   - Download from https://trufflesuite.com/ganache/
   - Create a new workspace with RPC Server at http://127.0.0.1:8545
   
2. Update your settings to use the local node:
   ```python
   # In settings.py
   ETH_NETWORK_URL = "http://127.0.0.1:8545"
   ETH_CHAIN_ID = 1337  # Ganache chain ID
   ```

3. Deploy your contract to the local network:
   ```bash
   cd ethereum
   npx hardhat run scripts/deploy.js --network localhost
   ``` 
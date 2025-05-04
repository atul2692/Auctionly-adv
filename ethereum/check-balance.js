// Script to check wallet balance on Sepolia
const { ethers } = require("hardhat");

async function main() {
  try {
    console.log("Checking account balance on Sepolia network...");
    
    // Get the current account
    const [account] = await ethers.getSigners();
    console.log(`Account address: ${account.address}`);
    
    // Get and display balance
    const balance = await ethers.provider.getBalance(account.address);
    console.log(`Account balance: ${ethers.formatEther(balance)} ETH`);
    
    if (balance.toString() === "0") {
      console.log("\n==== ATTENTION: ZERO BALANCE DETECTED ====");
      console.log("Your account has no ETH on Sepolia testnet.");
      console.log("Please get test ETH from a Sepolia faucet:");
      console.log("1. Visit https://sepoliafaucet.com/ or https://sepolia-faucet.pk910.de/");
      console.log("2. Enter your wallet address: " + account.address);
      console.log("3. Follow the instructions to receive test ETH");
      console.log("4. Wait a few minutes for the transaction to be confirmed");
      console.log("5. Run this script again to check your balance");
    } else {
      console.log("✅ Your account has sufficient ETH to deploy contracts!");
      console.log("You can now deploy your contracts with:");
      console.log("npx hardhat run scripts/deploy-v2.js --network sepolia");
    }
  } catch (error) {
    console.error("Error checking balance:", error);
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch(error => {
    console.error(error);
    process.exit(1);
  }); 
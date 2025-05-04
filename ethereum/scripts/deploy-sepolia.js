// Deploy script for the auction system contracts on Sepolia testnet
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Deploying contracts to Sepolia testnet...");
  
  // Check if we have the required environment variables
  if (!process.env.INFURA_SEPOLIA_URL) {
    console.error("ERROR: Missing INFURA_SEPOLIA_URL environment variable");
    console.log("Set it with: export INFURA_SEPOLIA_URL='https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID'");
    process.exit(1);
  }
  
  if (!process.env.PRIVATE_KEY) {
    console.error("ERROR: Missing PRIVATE_KEY environment variable");
    console.log("Set it with: export PRIVATE_KEY='your_ethereum_private_key'");
    process.exit(1);
  }
  
  console.log("Network: Sepolia Testnet");
  
  // Get the network info
  const [deployer] = await ethers.getSigners();
  console.log(`Deploying contracts with the account: ${deployer.address}`);
  console.log(`Account balance: ${(await deployer.getBalance()).toString()}`);
  
  // Deploy the AuctionContract
  console.log("Deploying AuctionContract...");
  const AuctionContract = await ethers.getContractFactory("AuctionContract");
  const auctionContract = await AuctionContract.deploy();
  await auctionContract.deployed();
  console.log(`AuctionContract deployed to: ${auctionContract.address}`);
  
  // Deploy the PaymentProcessor contract
  console.log("Deploying PaymentProcessor...");
  const PaymentProcessor = await ethers.getContractFactory("PaymentProcessor");
  const paymentProcessor = await PaymentProcessor.deploy(auctionContract.address);
  await paymentProcessor.deployed();
  console.log(`PaymentProcessor deployed to: ${paymentProcessor.address}`);
  
  // Save deployment information to a file
  const deploymentInfo = {
    network: "sepolia",
    chainId: 11155111,
    auctionContract: auctionContract.address,
    paymentProcessor: paymentProcessor.address,
    deploymentTime: new Date().toISOString()
  };
  
  const deploymentPath = path.join(__dirname, "..", "deployment-sepolia.json");
  fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
  console.log(`Deployment information saved to ${deploymentPath}`);
  
  // Print instructions for updating settings.py
  console.log("\n== NEXT STEPS ==");
  console.log("1. Update your Django settings.py with the deployed contract address:");
  console.log(`   AUCTION_CONTRACT_ADDRESS = "${auctionContract.address}"`);
  console.log("2. Test your connection to the Sepolia testnet");
  
  console.log("\nDeployment complete!");
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 
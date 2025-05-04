// Simple deployment script for Sepolia
const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  // Print deployment info
  console.log("Deploying contracts to Sepolia testnet...");
  console.log(`Using Infura URL: ${process.env.INFURA_SEPOLIA_URL || "Not set"}`);
  
  try {
    // Get the deployer account
    const [deployer] = await ethers.getSigners();
    console.log(`Deploying with account: ${deployer.address}`);
    
    // Deploy AuctionContract
    console.log("Deploying AuctionContract...");
    const AuctionContract = await ethers.getContractFactory("AuctionContract");
    const auction = await AuctionContract.deploy();
    await auction.deployed();
    
    console.log(`AuctionContract deployed to: ${auction.address}`);
    
    // Deploy PaymentProcessor
    console.log("Deploying PaymentProcessor...");
    const PaymentProcessor = await ethers.getContractFactory("PaymentProcessor");
    const payment = await PaymentProcessor.deploy(auction.address);
    await payment.deployed();
    
    console.log(`PaymentProcessor deployed to: ${payment.address}`);
    
    // Save deployment info
    const deployData = {
      network: "sepolia",
      deployer: deployer.address,
      auctionContract: auction.address,
      paymentProcessor: payment.address,
      timestamp: new Date().toISOString()
    };
    
    fs.writeFileSync(
      path.join(__dirname, "../deployment-info.json"),
      JSON.stringify(deployData, null, 2)
    );
    
    console.log("Deployment successful!");
    console.log("\nUpdate your Django settings with:");
    console.log(`AUCTION_CONTRACT_ADDRESS = "${auction.address}"`);
  } catch (error) {
    console.error("Deployment failed:");
    console.error(error);
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch(error => {
    console.error(error);
    process.exit(1);
  }); 
// Deployment script for Hardhat v2.23.0 and Ethers v6
const fs = require("fs");
const path = require("path");

async function main() {
  try {
    console.log("Starting deployment to Sepolia network...");
    
    // Get signer info
    const [deployer] = await ethers.getSigners();
    console.log(`Deploying contracts with account: ${deployer.address}`);
    
    const balance = await ethers.provider.getBalance(deployer.address);
    console.log(`Account balance: ${ethers.formatEther(balance)} ETH`);
    
    // Deploy AuctionContract
    console.log("Deploying AuctionContract...");
    const AuctionContract = await ethers.getContractFactory("AuctionContract");
    const auction = await AuctionContract.deploy();
    console.log(`AuctionContract deployment transaction: ${auction.deploymentTransaction().hash}`);
    console.log("Waiting for deployment to complete...");
    
    await auction.waitForDeployment();
    const auctionAddress = await auction.getAddress();
    console.log(`AuctionContract deployed to: ${auctionAddress}`);
    
    // Deploy PaymentProcessor
    console.log("Deploying PaymentProcessor...");
    const PaymentProcessor = await ethers.getContractFactory("PaymentProcessor");
    const processor = await PaymentProcessor.deploy(auctionAddress);
    console.log(`PaymentProcessor deployment transaction: ${processor.deploymentTransaction().hash}`);
    console.log("Waiting for deployment to complete...");
    
    await processor.waitForDeployment();
    const processorAddress = await processor.getAddress();
    console.log(`PaymentProcessor deployed to: ${processorAddress}`);
    
    // Save deployment information
    const deploymentInfo = {
      network: "sepolia",
      chainId: 11155111,
      deployer: deployer.address,
      auctionContract: auctionAddress,
      paymentProcessor: processorAddress,
      deploymentTime: new Date().toISOString()
    };
    
    const deploymentPath = path.join(__dirname, "..", "deployment-info.json");
    fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
    console.log(`Deployment information saved to ${deploymentPath}`);
    
    // Instructions
    console.log("\n=== NEXT STEPS ===");
    console.log("Update your Django settings with the following:");
    console.log(`AUCTION_CONTRACT_ADDRESS = "${auctionAddress}"`);
    console.log("\nDeployment successful!");
    
  } catch (error) {
    console.error("Deployment failed:");
    console.error(error);
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 
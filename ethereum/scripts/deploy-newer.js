// Deployment script for newer Hardhat versions
async function main() {
  try {
    console.log("Starting deployment to Sepolia network...");
    
    // Get the hardhat runtime environment
    const hre = require("hardhat");
    
    console.log("Checking deployer account...");
    const deployer = (await hre.ethers.getSigners())[0];
    console.log(`Deployer account address: ${deployer.address}`);
    
    // Deploy AuctionContract
    console.log("Deploying AuctionContract...");
    const AuctionContractFactory = await hre.ethers.getContractFactory("AuctionContract", deployer);
    const auctionContract = await AuctionContractFactory.deploy();
    await auctionContract.deployed();
    console.log(`AuctionContract deployed to: ${auctionContract.address}`);
    
    // Deploy PaymentProcessor
    console.log("Deploying PaymentProcessor...");
    const PaymentProcessorFactory = await hre.ethers.getContractFactory("PaymentProcessor", deployer);
    const paymentProcessor = await PaymentProcessorFactory.deploy(auctionContract.address);
    await paymentProcessor.deployed();
    console.log(`PaymentProcessor deployed to: ${paymentProcessor.address}`);
    
    // Save the deployment info
    const fs = require("fs");
    const path = require("path");
    const deploymentInfo = {
      network: "sepolia",
      auctionContract: auctionContract.address,
      paymentProcessor: paymentProcessor.address,
      deployer: deployer.address,
      timestamp: new Date().toISOString()
    };
    
    const deploymentPath = path.join(__dirname, "../deployment-info.json");
    fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
    console.log(`Deployment information saved to ${deploymentPath}`);
    
    console.log("\n==== DEPLOYMENT COMPLETED SUCCESSFULLY ====");
    console.log("\nUpdate your Django settings with:");
    console.log(`AUCTION_CONTRACT_ADDRESS = "${auctionContract.address}"`);
    
  } catch (error) {
    console.error("Deployment failed with error:");
    console.error(error);
    process.exit(1);
  }
}

// Run the deployment
main()
  .then(() => process.exit(0))
  .catch(error => {
    console.error(error);
    process.exit(1);
  }); 
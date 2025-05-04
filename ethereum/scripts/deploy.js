// Deploy script for the auction system contracts
const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying contracts...");
  
  // Deploy the AuctionContract
  const AuctionContract = await ethers.getContractFactory("AuctionContract");
  const auctionContract = await AuctionContract.deploy();
  await auctionContract.deployed();
  console.log(`AuctionContract deployed to: ${auctionContract.address}`);
  
  // Deploy the PaymentProcessor contract
  const PaymentProcessor = await ethers.getContractFactory("PaymentProcessor");
  const paymentProcessor = await PaymentProcessor.deploy(auctionContract.address);
  await paymentProcessor.deployed();
  console.log(`PaymentProcessor deployed to: ${paymentProcessor.address}`);
  
  console.log("Deployment complete!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 
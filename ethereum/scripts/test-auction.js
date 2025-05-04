// Test script for interacting with the deployed auction contracts
const { ethers } = require("hardhat");

async function main() {
  console.log("Testing Auction Contracts...");
  
  // Get the contract addresses (replace with your deployed contract addresses)
  const AUCTION_CONTRACT_ADDRESS = "YOUR_AUCTION_CONTRACT_ADDRESS";
  const PAYMENT_PROCESSOR_ADDRESS = "YOUR_PAYMENT_PROCESSOR_ADDRESS";
  
  // Get signers (accounts)
  const [deployer, seller, bidder1, bidder2] = await ethers.getSigners();
  
  console.log("Using accounts:");
  console.log(`Deployer: ${deployer.address}`);
  console.log(`Seller: ${seller.address}`);
  console.log(`Bidder 1: ${bidder1.address}`);
  console.log(`Bidder 2: ${bidder2.address}`);
  
  // Get contract instances
  const auctionContract = await ethers.getContractAt("AuctionContract", AUCTION_CONTRACT_ADDRESS);
  const paymentProcessor = await ethers.getContractAt("PaymentProcessor", PAYMENT_PROCESSOR_ADDRESS);
  
  console.log("\n1. Creating a new auction...");
  
  // Get the current timestamp
  const currentTime = Math.floor(Date.now() / 1000);
  
  // Set auction to end in 1 hour
  const endTime = currentTime + 3600;
  
  // Starting price: 1 ETH (in wei)
  const startingPrice = ethers.utils.parseEther("1.0");
  
  // Create a new auction (as the seller)
  const createTx = await auctionContract.connect(seller).createAuction(endTime, startingPrice);
  await createTx.wait();
  
  // Get the auction ID from the event
  const auctionId = 0; // First auction ID is 0
  console.log(`Created auction with ID: ${auctionId}`);
  
  console.log("\n2. Placing bids...");
  
  // Bidder 1 places a bid (1.1 ETH)
  const bid1Amount = ethers.utils.parseEther("1.1");
  const bid1Tx = await auctionContract.connect(bidder1).placeBid(auctionId, { value: bid1Amount });
  await bid1Tx.wait();
  console.log(`Bidder 1 placed a bid of ${ethers.utils.formatEther(bid1Amount)} ETH`);
  
  // Bidder 2 places a higher bid (1.2 ETH)
  const bid2Amount = ethers.utils.parseEther("1.2");
  const bid2Tx = await auctionContract.connect(bidder2).placeBid(auctionId, { value: bid2Amount });
  await bid2Tx.wait();
  console.log(`Bidder 2 placed a bid of ${ethers.utils.formatEther(bid2Amount)} ETH`);
  
  console.log("\n3. Getting auction details...");
  const auctionDetails = await auctionContract.getAuction(auctionId);
  console.log(`Seller: ${auctionDetails.seller}`);
  console.log(`Current Highest Bid: ${ethers.utils.formatEther(auctionDetails.currentPrice)} ETH`);
  console.log(`Highest Bidder: ${auctionDetails.highestBidder}`);
  console.log(`End Time: ${new Date(auctionDetails.endTime * 1000).toLocaleString()}`);
  
  // To test the complete flow in a real scenario, you would:
  // 1. Wait for the auction to end
  // 2. Call endAuction
  // 3. Make payment through the payment processor
  // 4. Withdraw funds as the seller
  
  console.log("\nTest completed!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 
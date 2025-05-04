// Script to test interaction with the deployed contract on Sepolia
const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  try {
    console.log("Testing deployed contract on Sepolia...");
    
    // Read deployment info
    const deploymentPath = path.join(__dirname, "deployment-info.json");
    let deploymentInfo;
    
    try {
      deploymentInfo = JSON.parse(fs.readFileSync(deploymentPath, 'utf8'));
      console.log("Deployment info loaded successfully");
    } catch (error) {
      console.error("Error reading deployment info:", error);
      process.exit(1);
    }
    
    // Get signer
    const [account] = await ethers.getSigners();
    console.log(`Using account: ${account.address}`);
    
    // Create contract instance
    const auctionAddress = deploymentInfo.auctionContract;
    console.log(`Connecting to AuctionContract at: ${auctionAddress}`);
    
    // Get the AuctionContract ABI
    const auctionAbi = [
      // Only need a few functions for testing
      "function createAuction(uint256 _endTime, uint256 _startingPrice) external returns (uint256)",
      "function getAuction(uint256 _auctionId) external view returns (address seller, uint256 startingPrice, uint256 currentPrice, address highestBidder, uint256 endTime, bool ended, bool paid)"
    ];
    
    const contract = new ethers.Contract(auctionAddress, auctionAbi, account);
    
    // Test reading contract state (doesn't make changes)
    console.log("Testing contract read operation...");
    
    try {
      // Try to read auction #0 (may not exist)
      const auction = await contract.getAuction(0);
      console.log("Auction #0 details:");
      console.log("- Seller:", auction.seller);
      console.log("- Starting price:", ethers.formatUnits(auction.startingPrice, 'ether'), "ETH");
      console.log("- Current price:", ethers.formatUnits(auction.currentPrice, 'ether'), "ETH");
      console.log("- Highest bidder:", auction.highestBidder);
      console.log("- End time:", new Date(Number(auction.endTime) * 1000).toLocaleString());
      console.log("- Ended:", auction.ended);
      console.log("- Paid:", auction.paid);
    } catch (error) {
      console.log("Auction #0 doesn't exist yet or cannot be accessed");
    }
    
    console.log("\nWould you like to create a test auction? (This will cost gas)");
    console.log("To create a test auction, run the following command:");
    console.log('npx hardhat run scripts/create-test-auction.js --network sepolia');
    
    console.log("\nContract test completed successfully!");
    
  } catch (error) {
    console.error("Error testing contract:", error);
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 
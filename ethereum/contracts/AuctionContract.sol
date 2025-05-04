// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AuctionContract
 * @dev Smart contract for handling Ethereum auctions
 */
contract AuctionContract {
    // Auction structure
    struct Auction {
        uint256 id;
        address payable seller;
        uint256 startingPrice;
        uint256 currentPrice;
        address payable highestBidder;
        uint256 endTime;
        bool ended;
        bool paid;
    }

    // Mapping of auction ID to Auction struct
    mapping(uint256 => Auction) public auctions;
    
    // Counter for generating unique auction IDs
    uint256 private _auctionIdCounter;
    
    // Events
    event AuctionCreated(uint256 indexed auctionId, address indexed seller, uint256 startingPrice, uint256 endTime);
    event BidPlaced(uint256 indexed auctionId, address indexed bidder, uint256 amount);
    event AuctionEnded(uint256 indexed auctionId, address indexed winner, uint256 amount);
    event PaymentReceived(uint256 indexed auctionId, address indexed buyer, uint256 amount);
    event FundsWithdrawn(uint256 indexed auctionId, address indexed seller, uint256 amount);
    
    /**
     * @dev Create a new auction
     * @param _endTime Timestamp when the auction will end
     * @param _startingPrice Minimum bid price in wei
     * @return auctionId Unique identifier for the created auction
     */
    function createAuction(uint256 _endTime, uint256 _startingPrice) external returns (uint256) {
        require(_endTime > block.timestamp, "End time must be in the future");
        require(_startingPrice > 0, "Starting price must be greater than 0");
        
        uint256 auctionId = _auctionIdCounter++;
        
        auctions[auctionId] = Auction({
            id: auctionId,
            seller: payable(msg.sender),
            startingPrice: _startingPrice,
            currentPrice: _startingPrice,
            highestBidder: payable(address(0)),
            endTime: _endTime,
            ended: false,
            paid: false
        });
        
        emit AuctionCreated(auctionId, msg.sender, _startingPrice, _endTime);
        
        return auctionId;
    }
    
    /**
     * @dev Place a bid on an auction
     * @param _auctionId ID of the auction to bid on
     */
    function placeBid(uint256 _auctionId) external payable {
        Auction storage auction = auctions[_auctionId];
        
        require(block.timestamp < auction.endTime, "Auction has ended");
        require(!auction.ended, "Auction already finalized");
        require(msg.sender != auction.seller, "Seller cannot bid on their own auction");
        require(msg.value > auction.currentPrice, "Bid must be higher than current price");
        
        // Refund the previous highest bidder
        if (auction.highestBidder != address(0)) {
            (bool success, ) = auction.highestBidder.call{value: auction.currentPrice}("");
            require(success, "Failed to refund previous bidder");
        }
        
        // Update auction with new highest bid
        auction.highestBidder = payable(msg.sender);
        auction.currentPrice = msg.value;
        
        emit BidPlaced(_auctionId, msg.sender, msg.value);
    }
    
    /**
     * @dev End an auction and determine the winner
     * @param _auctionId ID of the auction to end
     */
    function endAuction(uint256 _auctionId) external {
        Auction storage auction = auctions[_auctionId];
        
        require(msg.sender == auction.seller, "Only seller can end the auction");
        require(block.timestamp >= auction.endTime, "Auction has not ended yet");
        require(!auction.ended, "Auction already ended");
        
        auction.ended = true;
        
        emit AuctionEnded(_auctionId, auction.highestBidder, auction.currentPrice);
    }
    
    /**
     * @dev Make payment for winning an auction
     * @param _auctionId ID of the auction to pay for
     */
    function makePayment(uint256 _auctionId) external payable {
        Auction storage auction = auctions[_auctionId];
        
        require(auction.ended, "Auction has not ended yet");
        require(msg.sender == auction.highestBidder, "Only highest bidder can make payment");
        require(!auction.paid, "Payment already made");
        require(msg.value >= auction.currentPrice, "Insufficient payment amount");
        
        auction.paid = true;
        
        emit PaymentReceived(_auctionId, msg.sender, msg.value);
    }
    
    /**
     * @dev Withdraw funds from a completed auction
     * @param _auctionId ID of the auction to withdraw funds from
     */
    function withdrawFunds(uint256 _auctionId) external {
        Auction storage auction = auctions[_auctionId];
        
        require(msg.sender == auction.seller, "Only seller can withdraw funds");
        require(auction.ended, "Auction has not ended yet");
        require(auction.paid, "Payment has not been made yet");
        
        uint256 amount = auction.currentPrice;
        
        // Reset the auction's current price to prevent re-entrancy
        auction.currentPrice = 0;
        
        (bool success, ) = auction.seller.call{value: amount}("");
        require(success, "Failed to transfer funds to seller");
        
        emit FundsWithdrawn(_auctionId, auction.seller, amount);
    }
    
    /**
     * @dev Get auction details
     * @param _auctionId ID of the auction
     * @return seller The address of the seller
     * @return startingPrice The starting price of the auction
     * @return currentPrice The current highest bid
     * @return highestBidder The address of the highest bidder
     * @return endTime The timestamp when the auction ends
     * @return ended Whether the auction has ended
     * @return paid Whether payment has been made
     */
    function getAuction(uint256 _auctionId) external view returns (
        address seller,
        uint256 startingPrice,
        uint256 currentPrice,
        address highestBidder,
        uint256 endTime,
        bool ended,
        bool paid
    ) {
        Auction storage auction = auctions[_auctionId];
        
        return (
            auction.seller,
            auction.startingPrice,
            auction.currentPrice,
            auction.highestBidder,
            auction.endTime,
            auction.ended,
            auction.paid
        );
    }
} 
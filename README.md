# AuctionHub - Online Auction Website

A responsive Django-based online auction platform with a modern UI, Ethereum blockchain integration, and payment processing.

## Features

- Responsive landing page with animations and modern UI
- Image slider for featured auctions
- Testimonials section
- Mobile-friendly design
- User authentication and account management
- Auction listing and bidding functionality
- Ethereum blockchain integration for auction verification
- Razorpay payment integration
- Celery for asynchronous task processing

## Technologies Used

- **Backend**: 
  - Django 5.2
  - Celery with Redis for asynchronous tasks
  - Web3.py for Ethereum integration
  - Razorpay for payment processing

- **Frontend**: 
  - HTML5, CSS3, JavaScript
  - Bootstrap 5
  - Font Awesome
  - AOS Animation Library
  - Swiper JS

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Auc-1
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv env
   .\env\Scripts\activate  # Windows
   source env/bin/activate  # Unix/MacOS
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env` 
   - Update the values in `.env` with your actual credentials

5. Install and start Redis (required for Celery):
   - Windows: Run `install_redis.ps1` PowerShell script then `start_redis.bat`
   - Linux/Mac: Install Redis through package manager and start the service

6. Run migrations:
   ```
   python manage.py migrate
   ```

7. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

8. Start Celery worker (in a separate terminal):
   ```
   # Windows:
   start_celery.bat
   
   # Linux/Mac:
   celery -A auction_site worker -l info
   ```

9. Start the development server:
   ```
   python manage.py runserver
   ```

10. Open your browser and navigate to: `http://127.0.0.1:8000/`

## Ethereum Integration

This project integrates with the Ethereum blockchain using the Sepolia testnet. To set up:

1. Create an Infura account and get an API key
2. Update the ETH_NETWORK_URL in your `.env` file
3. See `DEPLOYING_TO_SEPOLIA.md` for detailed instructions on deploying and interacting with smart contracts

## Project Structure

- `auction_site/` - Django project settings and configuration
- `home/` - App for the landing page and main site functionality
- `accounts/` - User authentication and profile management
- `auctions/` - Core auction functionality
- `ethereum/` - Blockchain integration components
- `static/` - Static assets (CSS, JS, images)
- `templates/` - HTML templates
- `scripts/` - Utility scripts
- `media/` - User-uploaded content

## Development

### Running Tests

```
python manage.py test
```

### Generating Sample Data

Several scripts are available to generate sample data:
- `create_categories.py` - Create auction categories
- `create_sample_auction.py` - Create a sample auction
- `create_multiple_auctions.py` - Create multiple auctions
- `populate_categories.py` - Populate categories with data

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
from django.urls import path
from . import views, views_eth

app_name = 'auctions'

urlpatterns = [
    path('', views.auction_list, name='auction_list'),
    path('categories/', views.categories, name='categories'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('create/', views.create_auction, name='create_auction'),
    path('my-auctions/', views.my_auctions, name='my_auctions'),
    path('my-bids/', views.my_bids, name='my_bids'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('image/<int:pk>/delete/', views.delete_auction_image, name='delete_auction_image'),
    path('<slug:slug>/', views.auction_detail, name='auction_detail'),
    path('<slug:slug>/edit/', views.edit_auction, name='edit_auction'),
    path('<slug:slug>/delete/', views.delete_auction, name='delete_auction'),
    path('<slug:slug>/bid/', views.place_bid, name='place_bid'),
    path('<slug:slug>/watchlist/', views.toggle_watchlist, name='toggle_watchlist'),
    
    # Ethereum payment URLs
    path('<slug:slug>/payment/', views_eth.auction_payment, name='auction_payment'),
    path('<slug:slug>/process-payment/', views_eth.process_eth_payment, name='process_eth_payment'),
    
    # Razorpay payment URLs
    path('<slug:slug>/razorpay-payment/', views.razorpay_payment, name='razorpay_payment'),
    path('<slug:slug>/razorpay-callback/', views.razorpay_callback, name='razorpay_callback'),
    
    # Ethereum API endpoints
    path('api/auction/<slug:slug>/eth-details/', views_eth.get_auction_eth_details, name='auction_eth_details'),
    path('auction/<int:auction_id>/sync-blockchain/', views_eth.sync_auction_blockchain, name='sync_blockchain'),
    
    # API endpoint to process ended auctions
    path('api/process-ended-auction/<slug:slug>/', views.process_ended_auction, name='process_ended_auction'),
] 
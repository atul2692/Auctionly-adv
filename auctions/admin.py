from django.contrib import admin
from .models import Category, Auction, AuctionImage, Bid, Watchlist

class AuctionImageInline(admin.TabularInline):
    model = AuctionImage
    extra = 1

class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    readonly_fields = ('bidder', 'amount', 'created_at')
    can_delete = False
    max_num = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'current_price', 'status', 'end_date', 'featured')
    list_filter = ('status', 'featured', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'views_count', 'bid_count')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'seller', 'category', 'description')}),
        ('Price Information', {'fields': ('starting_price', 'current_price')}),
        ('Images', {'fields': ('image', 'additional_images')}),
        ('Auction Settings', {'fields': ('end_date', 'status', 'featured')}),
        ('Statistics', {'fields': ('views_count', 'created_at', 'updated_at')}),
    )
    inlines = [AuctionImageInline, BidInline]

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('auction', 'bidder', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('auction__title', 'bidder__username')
    readonly_fields = ('auction', 'bidder', 'amount', 'created_at')

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'auction', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'auction__title')

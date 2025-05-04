from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Auction, Bid, Category, AuctionImage

class AuctionForm(forms.ModelForm):
    """
    Form for creating and editing auction listings
    """
    class Meta:
        model = Auction
        fields = [
            'title', 'category', 'description', 'starting_price', 
            'image', 'end_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter auction title'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your item in detail'}),
            'starting_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter starting price'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def clean_end_date(self):
        """
        Validate that the end date is in the future
        """
        end_date = self.cleaned_data.get('end_date')
        if end_date and end_date <= timezone.now():
            raise ValidationError('End date must be in the future.')
        return end_date
    
    def clean_starting_price(self):
        """
        Validate that the starting price is positive
        """
        starting_price = self.cleaned_data.get('starting_price')
        if starting_price and starting_price <= 0:
            raise ValidationError('Starting price must be greater than zero.')
        return starting_price


class AuctionImageForm(forms.ModelForm):
    """
    Form for additional auction images
    """
    class Meta:
        model = AuctionImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }


class BidForm(forms.ModelForm):
    """
    Form for placing bids on auctions
    """
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your bid amount',
                'step': '0.01'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.auction = kwargs.pop('auction', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_amount(self):
        """
        Validate that the bid amount is higher than the current price
        """
        amount = self.cleaned_data.get('amount')
        
        if not self.auction:
            raise ValidationError('Auction not found.')
        
        if amount <= self.auction.current_price:
            raise ValidationError(f'Your bid must be higher than the current price (${self.auction.current_price}).')
        
        return amount 
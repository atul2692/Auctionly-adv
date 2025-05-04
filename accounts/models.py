from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Custom User model with user type for differentiating between customers and sellers
    """
    USER_TYPE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('SELLER', 'Seller'),
    )
    
    user_type = models.CharField(
        _('User Type'),
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='CUSTOMER',
    )
    
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    verification_token = models.CharField(max_length=100, null=True, blank=True)
    
    # Define fields that are required when creating a user
    REQUIRED_FIELDS = ['email', 'user_type']
    
    def __str__(self):
        return self.username
    
    @property
    def is_customer(self):
        return self.user_type == 'CUSTOMER'
    
    @property
    def is_seller(self):
        return self.user_type == 'SELLER'

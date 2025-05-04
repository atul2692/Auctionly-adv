from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()

class UserLoginForm(AuthenticationForm):
    """
    Form for user login with custom styling
    """
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'autocomplete': 'off',
            }
        )
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password',
            }
        )
    )

    class Meta:
        model = User
        fields = ['username', 'password']


class UserRegisterForm(UserCreationForm):
    """
    Form for user registration with password strength validation
    """
    USER_TYPE_CHOICES = (
        ('CUSTOMER', 'Register as Customer'),
        ('SELLER', 'Register as Seller'),
    )
    
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'autocomplete': 'off',
            }
        )
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'autocomplete': 'off',
            }
        )
    )
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(
            attrs={
                'class': 'form-check-input',
            }
        ),
        initial='CUSTOMER',
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password',
            }
        )
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm Password',
            }
        )
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'password1', 'password2']
    
    def clean_password1(self):
        """
        Validate that the password meets the minimum requirements
        - At least 8 characters
        - At least one uppercase letter
        - At least one special character
        - At least one number
        """
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one number.')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).')
        
        return password
    
    def clean_email(self):
        """
        Validate that the email address is unique
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already in use.')
        
        return email


class UserProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile
    """
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
            }
        )
    )
    
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
            }
        )
    )
    
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Address',
                'rows': 3,
            }
        )
    )
    
    class Meta:
        model = User
        fields = ['profile_picture', 'phone_number', 'address'] 
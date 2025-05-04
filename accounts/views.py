from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
import uuid
from django.contrib.auth.tokens import default_token_generator
from django.db.models.query_utils import Q

from .forms import UserRegisterForm, UserLoginForm, UserProfileUpdateForm
from .tokens import account_activation_token

User = get_user_model()

def login_view(request):
    """
    View for user login
    """
    if request.user.is_authenticated:
        return redirect('home:index')
    
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'home:index')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """
    View for user registration with email verification using UUID4
    """
    if request.user.is_authenticated:
        return redirect('home:index')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Set user as inactive until email is verified
            
            # Generate UUID4 token
            verification_token = str(uuid.uuid4())
            user.verification_token = verification_token
            user.save()
            
            # Send email verification
            current_site = get_current_site(request)
            mail_subject = 'Activate your Auctionly account'
            message = render_to_string('accounts/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': verification_token,
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                subject=mail_subject, 
                body=message, 
                from_email='management.auctionly@gmail.com',
                to=[to_email]
            )
            email.content_subtype = "html"  # Set content type to HTML
            email.send()
            
            messages.success(request, 'Account created successfully! Please check your email to activate your account.')
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def activate_account(request, uidb64, token):
    """
    View to activate a user account via email verification using UUID4
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and user.verification_token == token:
        user.is_active = True
        user.verification_token = None  # Clear the token after use
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been activated!')
        return redirect('home:index')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('accounts:login')


def logout_view(request):
    """
    View for user logout
    """
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home:index')


@login_required
def profile_view(request):
    """
    View for user profile
    """
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


def seller_profile_view(request, seller_id):
    """
    View for seller profile page
    Displays seller information and their active auctions
    """
    seller = get_object_or_404(User, id=seller_id, user_type='SELLER')
    
    # Get seller's active auctions
    active_auctions = seller.auctions.filter(status='ACTIVE').order_by('-created_at')
    
    # Get seller's ended auctions
    ended_auctions = seller.auctions.filter(status='CLOSED').order_by('-end_date')[:5]
    
    # Calculate seller stats
    total_auctions = seller.auctions.count()
    successful_auctions = seller.auctions.filter(status='CLOSED', winner__isnull=False).count()
    success_rate = (successful_auctions / total_auctions * 100) if total_auctions > 0 else 0
    
    context = {
        'seller': seller,
        'active_auctions': active_auctions,
        'ended_auctions': ended_auctions,
        'total_auctions': total_auctions,
        'successful_auctions': successful_auctions,
        'success_rate': success_rate,
    }
    
    return render(request, 'accounts/seller_profile.html', context)

def password_reset_request(request):
    """
    View for password reset request
    """
    if request.user.is_authenticated:
        return redirect('home:index')
        
    if request.method == 'POST':
        email = request.POST.get('email', '')
        
        # Check if a user exists with this email
        users = User.objects.filter(Q(email=email) & Q(is_active=True))
        
        if users.exists():
            user = users.first()
            # Generate password reset token
            token = default_token_generator.make_token(user)
            
            # Send password reset email
            current_site = get_current_site(request)
            mail_subject = 'Reset your Auctionly password'
            message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token,
                'protocol': 'https' if request.is_secure() else 'http',
            })
            email = EmailMessage(
                subject=mail_subject, 
                body=message, 
                from_email='management.auctionly@gmail.com',
                to=[user.email]
            )
            email.content_subtype = "html"  # Set content type to HTML
            email.send()
        
        # Always show success message to prevent email enumeration
        return redirect('accounts:password_reset_done')
    
    return render(request, 'accounts/password_reset.html')

def password_reset_done(request):
    """
    View for password reset done page
    """
    if request.user.is_authenticated:
        return redirect('home:index')
        
    return render(request, 'accounts/password_reset_sent.html')

def password_reset_confirm(request, uidb64, token):
    """
    View for password reset confirmation
    """
    if request.user.is_authenticated:
        return redirect('home:index')
        
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # Check if the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        validlink = True
        
        if request.method == 'POST':
            # Process the form submission
            new_password1 = request.POST.get('new_password1', '')
            new_password2 = request.POST.get('new_password2', '')
            
            if not new_password1:
                messages.error(request, 'Please enter a new password.')
            elif not new_password2:
                messages.error(request, 'Please confirm your new password.')
            elif new_password1 != new_password2:
                messages.error(request, 'The two password fields did not match. Please try again.')
            elif len(new_password1) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
            elif not any(char.isupper() for char in new_password1):
                messages.error(request, 'Password must contain at least one uppercase letter.')
            elif not any(char.isdigit() for char in new_password1):
                messages.error(request, 'Password must contain at least one number.')
            elif not any(char in '!@#$%^&*(),.?":{}|<>' for char in new_password1):
                messages.error(request, 'Password must contain at least one special character.')
            else:
                # Set the new password and save the user
                user.set_password(new_password1)
                user.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('accounts:password_reset_complete')
    else:
        validlink = False
    
    return render(request, 'accounts/password_reset_confirm.html', {
        'validlink': validlink,
    })

def password_reset_complete(request):
    """
    View for password reset complete page
    """
    if request.user.is_authenticated:
        return redirect('home:index')
        
    return render(request, 'accounts/password_reset_complete.html')

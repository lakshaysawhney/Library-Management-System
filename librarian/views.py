from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from librarian.forms import BookForm
from librarian.models import Book
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_backends, get_user_model
from .forms import SignUpForm
from .models import UserProfile
from django.contrib import messages
from django.urls import reverse
import pyotp
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from .utils import send_otp_via_sms, send_otp_via_email
from twilio.base.exceptions import TwilioRestException
 
# Create your views here.

def home(request):
    return render(request, 'librarian/home.html')

###################################################################################

@login_required
def book_create(request):
    form = BookForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('all_books')
    return render(request, 'librarian/book_form.html', {'form':form}) 

@login_required 
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)   
    form = BookForm(request.POST or None, instance = book)
    if form.is_valid():
        form.save()
        return redirect('all_books')
    return render(request, 'librarian/book_form.html', {'form': form})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('all_books')
    return render(request, 'librarian/book_confirm_delete.html', {'book': book})

###################################################################################

@login_required
# for students
def available_books(request):
    if request.user.is_librarian:
        return redirect('login') 
    books = Book.objects.filter(available=True, issued=False)
    return render(request, 'librarian/available_books.html', {'books': books})

@login_required
def issue_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.available and not book.issued:
        book.available = False
        book.issued = True
        book.issued_to = request.user
        book.due_date = datetime.now().date() + timedelta(days=7)
        book.save()
    return redirect('issued_books')

@login_required
def return_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.issued_to == request.user:
        book.available = True
        book.issued = False
        book.issued_to = None
        book.save()
    return redirect('available_books')

@login_required
# for a particular student
def issued_books(request):
    books = Book.objects.filter(issued_to=request.user)
    return render(request, 'librarian/issued_books.html', {'books': books})

@login_required
def all_books(request):
    if request.user.is_librarian:
        books = Book.objects.all()
        return render(request, 'librarian/all_books.html', {'books': books})
    else:
        return redirect('login')   
###################################################################################

from django.contrib.auth import login, get_backends
from django.shortcuts import render, redirect
from .forms import SignUpForm
from .models import UserProfile
from .utils import send_otp_via_email, send_otp_via_sms  

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Get the first authentication backend
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, user, backend=user.backend)
            
            # Generate OTP
            otp = user.generate_otp()
            
            # Send OTP via email
            send_otp_via_email(user.email, otp)
            
            try:
                # Send OTP via SMS
                send_otp_via_sms(user.phone_number, otp)
            except TwilioRestException as e:
                # Log the error and provide feedback to the user
                print(f"Twilio error: {e}")
                form.add_error('phone_number', 'Failed to send SMS. Please check the phone number.')
                return render(request, 'librarian/signup.html', {'form': form})

            return redirect('verify_otp')
        else:
            print(form.errors)
    else:
        form = SignUpForm()
    
    return render(request, 'librarian/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_librarian:
                return redirect('all_books')
            else:
                return redirect('available_books')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'librarian/login.html') 

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        print(f"OTP entered: {otp}")  # Debugging line
        is_valid = request.user.verify_otp(otp)
        print(f"OTP valid: {is_valid}")  # Debugging line
        if is_valid:
            messages.success(request, 'OTP verified successfully.')
            print("OTP verified")  # Debugging line
            return redirect('login') 
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            print("Invalid OTP")  # Debugging line
    else:
        print("Not a POST request")  # Debugging line
    return render(request, 'librarian/verify_otp.html')

##################################################################################

UserProfile = get_user_model()

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = UserProfile.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    otp = pyotp.TOTP(pyotp.random_base32()).now()
                    user.otp_code = otp
                    user.save()
                    send_otp_via_email(user.email, otp)
                    send_otp_via_sms(user.phone_number, otp)
                messages.success(request, 'An OTP has been sent to your email and phone number.')
                return redirect('verify_otp_reset')
            else:
                messages.error(request, 'No user is associated with this email address.')
    else:
        form = PasswordResetForm()
    return render(request, 'librarian/password_reset.html', {'form': form})

def verify_otp_reset(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user_profile = UserProfile.objects.filter(otp_code=otp).first()
        if user_profile:
            user_profile.otp_code = ''  # Clear the OTP code
            user_profile.save()

            # Generate uid and token
            uid = urlsafe_base64_encode(force_bytes(user_profile.pk))
            token = default_token_generator.make_token(user_profile)

            messages.success(request, 'OTP verified successfully.')
            return redirect('password_reset_confirm', uidb64=uid, token=token)
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'librarian/verify_otp_reset.html')

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from .forms import RegistrationForm,UserProfileForm
from .models import Account,UserProfile
# Create your views here.
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.utils.encoding import force_str
import requests




from urllib.parse import urlparse, parse_qs

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from urllib.parse import urlparse, parse_qs

def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        remember_me = request.POST.get('remember_me')  # Get the 'remember_me' value from the form

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Log the user in
            auth_login(request, user)
            messages.success(request, "You are now logged in")

            # Handle 'Remember Me'
            if remember_me:  # If 'Remember Me' is checked
                request.session.set_expiry(604800)  # Session expires in 7 days (604800 seconds)
            else:
                request.session.set_expiry(0)  # Session expires when the browser is closed (default behavior)

            # Get the next parameter (redirect the user after login)
            next_page = request.GET.get('next','/show/naruto/') or request.POST.get('next')
            if next_page:
                return redirect(next_page)  # Redirect to the page user was originally trying to access

            # Fallback redirect if no 'next' parameter is found (redirect to dashboard or homepage)
            return redirect('home')

        else:
            # If the user authentication fails
            messages.error(request, 'Invalid login credentials')
            return redirect('login')  # Redirect back to login page for retry

    return render(request, 'login.html')  # Render the login page if the method is GET


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user_data = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'phone_number': form.cleaned_data['phone_number'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
                'username': form.cleaned_data['email'].split("@")[0],
            }
            
            # Store user data temporarily in session
            request.session['pending_user'] = user_data
            
            # Send activation email
            current_site = get_current_site(request)
            mail_subject = "Activate your account"
            message = render_to_string("account_verification.html", {
                "user": user_data['first_name'],
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user_data['email'])),
                "token": default_token_generator.make_token(Account()),
            })
            
            send_email = EmailMessage(mail_subject, message, to=[user_data['email']])
            send_email.content_subtype = "html"
            send_email.send()
            
            return redirect(f'/accounts/login/?command=verification&email={user_data["email"]}')
    else:
        form = RegistrationForm()
    return render(request, "register.html", {'form': form})


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request,'You have been logged out')
    return redirect('home')


def activate(request, uidb64, token):
    try:
        email = force_str(urlsafe_base64_decode(uidb64))
        user_data = request.session.get('pending_user')
        
        if not user_data or user_data['email'] != email:
            messages.error(request, "Activation link is invalid or expired.")
            return redirect("register")
        
        # Create user only after activation
        user = Account.objects.create_user(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            username=user_data['username'],
            password=user_data['password']
        )
        user.phone_number = user_data['phone_number']
        user.is_active = True  # Activate user
        user.save()
        
        del request.session['pending_user']  # Remove session data after activation
        messages.success(request, "Account activated successfully.")
        return redirect("login")
    except Exception as e:
        messages.error(request, "Activation failed.")
        return redirect("register")







def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            main_subject = "Reset Password"
            message = render_to_string("reset_password_email.html",{
                'user':user,
                'domain' : current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(main_subject,message,to=[to_email])
            send_email.content_subtype = "html"
            send_email.send()
            messages.success(request,"Password reset email has been sent to your email address")
            return redirect('login')
        else:
            messages.error(request,"Account doesnot exist")
            return redirect('forgotPassword')
    return render(request,'forgot_password.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except Exception as e:
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,"Please reset your password")
        return redirect('reset_password')
    else:
        messages.error(request,"This link has been expired")
        return redirect('login')
 
def resetPassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successful")
            return redirect('login')
        else:
            messages.error(request,"Password doesn't match")
            return redirect('reset_password')

    return render(request,'reset_password.html')


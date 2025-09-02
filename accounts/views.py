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

# Create your views here.

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
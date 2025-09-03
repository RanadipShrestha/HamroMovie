import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Show, Seat
from decimal import Decimal
import uuid
from accounts.models import Account
from django.urls import reverse
from django.utils import timezone
# Configure Stripe with secret key
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.db import transaction

def home(request):
    return render(request, 'home.html')


def show_seats(request, slug):
    show = Show.objects.get(slug=slug)
    hall = show.hall
    seats = Seat.objects.filter(show=show)
    context = {'show': show, 'hall': hall, 'seats': seats}
    return render(request, "show_seats.html", context)
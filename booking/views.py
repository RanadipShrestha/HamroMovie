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
def calculate_total_amount(seats):
    """Calculate the total price for selected seats."""
    total = Decimal('0.00')
    for seat in seats:
        total += seat.price  # Assuming each seat has a `price` field
    return total

def home(request):
    return render(request, 'home.html')

def show_seats(request, slug):
    show = Show.objects.get(slug=slug)
    hall = show.hall
    seats = Seat.objects.filter(show=show)
    context = {'show': show, 'hall': hall, 'seats': seats}
    return render(request, "show_seats.html", context)

import logging

logger = logging.getLogger(__name__)

def book_seats(request):
    if not request.user.is_authenticated:
        return redirect(f'{reverse("login")}?next={request.path}')
    
    print(f"Request method: {request.method}")  # Debugging line

    if request.method == 'POST':
        selected_seats = request.POST.getlist('selected_seats')
        if not selected_seats:
            return JsonResponse({'error': 'No seats selected.'})
        request.session['selected_seats'] = selected_seats
        return redirect('payment_page')
    
    return JsonResponse({'error': 'Invalid request method'})

def payment_page(request):
    """Initiate payment with Stripe."""
    if not request.user.is_authenticated:
        return redirect('login')
    selected_seats = request.session.get('selected_seats')
    if not selected_seats:
        return redirect('home')

    # Get seat details and calculate total amount
    seats = Seat.objects.filter(seat_number__in=selected_seats)
    total_amount = calculate_total_amount(seats)
    total_amount_cents = int(total_amount * 100)  # Convert to cents for Stripe

    # Create Stripe Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',  # Change currency as needed
                    'product_data': {
                        'name': 'Movie Ticket Booking',
                    },
                    'unit_amount': total_amount_cents,
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url=request.build_absolute_uri('/payment_success/'),
        cancel_url=request.build_absolute_uri('/payment_failure/'),
    )

    return redirect(session.url)

def payment_success(request):
    """Handle successful payment and mark seats as booked for the logged-in user."""
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    selected_seats = request.session.get('selected_seats', [])
    if not selected_seats:
        return redirect('home')
    with transaction.atomic():
        seats = Seat.objects.select_for_update().filter(seat_number__in=selected_seats)
    if any(seat.is_booked for seat in seats):
        return JsonResponse({'error': 'One or more seats are already booked. Please try again.'})

    # Retrieve the seat details and mark them as booked
    
    total_price = Decimal('0.00')
    for seat in seats:
        seat.is_booked = True
        seat.user = user # Associate seat with the logged-in user
        seat.save()
        total_price += seat.price  # Assuming `price` is a field in the Seat model

    # Clear selected seats in session
    request.session['selected_seats'] = []

    # Prepare the invoice data for the template
    invoice_data = {
        'customer_name': request.user.full_name(),
        'seats': seats,
        'total_price': total_price,
        'payment_status': 'Successful',
        'payment_date': timezone.now(),
    }

    return render(request, 'booking_success.html', {'invoice': invoice_data})

def payment_failure(request):
    """Handle failed payment."""
    return render(request,'payment_failure.html')

def movies(request):
    show = Show.objects.all()
    return render(request,'movie.html',{'show':show})

from collections import defaultdict

def reservation(request):
    if request.user.is_authenticated:
        # Fetch the booked seats for the current user
        booked_seats = Seat.objects.filter(user=request.user, is_booked=True)
        
        # Group the booked seats by movie
        grouped_seats = defaultdict(list)
        for seat in booked_seats:
            grouped_seats[seat.show.name].append(f"{seat.row}-{seat.seat_number}")
        
        # Join the seat numbers for each movie
        grouped_seats = {movie: ', '.join(seats) for movie, seats in grouped_seats.items()}

        return render(request, 'reservation.html', {'grouped_seats': grouped_seats})
    else:
        return redirect('login')
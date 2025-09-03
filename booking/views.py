import stripe
from django.shortcuts import render, redirect

from .models import Show, Seat



def home(request):
    return render(request, 'home.html')


def show_seats(request, slug):
    show = Show.objects.get(slug=slug)
    hall = show.hall
    seats = Seat.objects.filter(show=show)
    context = {'show': show, 'hall': hall, 'seats': seats}
    return render(request, "show_seats.html", context)
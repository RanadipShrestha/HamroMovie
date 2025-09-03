from django.urls import path
from . import views
urlpatterns= [
    path('',views.home,name="home"),
    path('reservation/',views.reservation,name="reservation"),
    path('movie_selection/',views.movies,name="movie_selection"),
    path('show/<slug:slug>/',views.show_seats,name='show_seats'),
    path('book-seats/',views.book_seats,name="book_seats"),
    path('payment/',views.payment_page,name="payment_page"),
    path('payment_success/',views.payment_success,name="payment_success"),
    path('payment_failure/',views.payment_failure,name="payment_failure"),
    path('payment-success/', views.payment_success, name='payment_success'),
]
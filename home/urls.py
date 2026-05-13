from django.urls import path
from .views import index, reservation, contact, blog, about
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from .views import dashboard, cancel_reservation, edit_reservation
from .views import confirm_payment
from django.contrib import admin
from .views import manager_dashboard

urlpatterns = [
    path('', index, name='index'),
    path('reservation/<int:room_id>/', reservation, name='reservation'),
    path('contact/', contact, name='contact'),    # Было "Contact"
    path('blog/', blog, name='blog'),             # Было "Blog"
    path('about/', about, name='about'),          # Было "About"
    path('dashboard/', dashboard, name='dashboard'),
    path('cancel/<int:pk>/', cancel_reservation, name='cancel_reservation'),
    path('edit/<int:pk>/', edit_reservation, name='edit_reservation'),
    path('confirm-payment/<int:pk>/', confirm_payment, name='confirm_payment'),
    path('manager/', manager_dashboard, name='manager_dashboard'),
]

urlpatterns += staticfiles_urlpatterns()

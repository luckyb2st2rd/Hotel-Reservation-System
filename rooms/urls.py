from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('allRooms/', views.allRooms, name='allRooms'),  # Добавлен trailing slash
]
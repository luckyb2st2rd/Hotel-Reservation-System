from django.urls import path
from .views import login_view, verify_2fa, register, logout, add_room
from .views import manager_dashboard
from .views import edit_room
from .views import delete_room, report_day, report_week, report_month

urlpatterns = [
    path('login/', login_view, name='login'),
    path('verify-2fa/', verify_2fa, name='verify_2fa'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('manager/dashboard/', manager_dashboard, name='manager_dashboard'),
    path('manager/room/add/', add_room, name='add_room'),
    path('manager/room/add/', add_room, name='add_room'),
    path('manager/room/<room_id>/edit/', edit_room, name='edit_room'),
    path('manager/room/<int:pk>/delete/', delete_room, name='delete_room'),
    path('manager/report/day/', report_day, name='report_day'),
    path('manager/report/week/', report_week, name='report_week'),
    path('manager/report/month/', report_month, name='report_month'),
]
from django.db import models
from django.contrib.auth.models import User
from rooms.models import Chambre
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your models here.

class Testimonial(models.Model):
    nom = models.CharField(max_length=20)
    avis = models.TextField()
    image = models.ImageField(upload_to='media/pics')

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

class Reservation(models.Model):
    Name = models.CharField(max_length=50)
    Surname = models.CharField(max_length=50)
    Phone = models.CharField(max_length=20)
    Email = models.EmailField(max_length=40)
    Date_Check_In = models.DateField(auto_now=False)
    Date_Check_Out  = models.DateField(auto_now=False)
    Note = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default='pending')  # pending / paid
    places = models.PositiveIntegerField(default=1)

    def total_price(self):
        nights = (self.Date_Check_Out - self.Date_Check_In).days
        return self.chambre.prix * nights

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

def __str__(self):
        return self.Name

User = get_user_model()

class ActionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    extra_data = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} — {self.action} — {self.timestamp.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        verbose_name = "Лог действия"
        verbose_name_plural = "Логи действий"
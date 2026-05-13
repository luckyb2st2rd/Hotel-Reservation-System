from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
# Create your models here.

class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        CLIENT = 'client', 'Клиент'
        MANAGER = 'manager', 'Менеджер'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.CLIENT)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

class Admin2FACode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f"Код для {self.user.email} — {self.code}"

    class Meta:
        verbose_name = "Код двухфакторной авторизации"
        verbose_name_plural = "Коды двухфакторной авторизации"
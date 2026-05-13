from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms
from rooms.models import Chambre

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", max_length=30, required=True)
    last_name = forms.CharField(label="Фамилия", max_length=30, required=True)
    email = forms.EmailField(required=True, label="Электронная почта")
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.role = 'client'
        if commit:
            user.save()
        return user

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Электронная почта", widget=forms.EmailInput(attrs={'autofocus': True}))

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                self.cleaned_data['username'] = user.username  # передаём логин по email
            except User.DoesNotExist:
                raise forms.ValidationError("Пользователь с такой почтой не найден.")
        return super().clean()

class ChambreForm(forms.ModelForm):
    class Meta:
        model = Chambre
        fields = ['nom', 'prix', 'image', 'description', 'disponibilité']
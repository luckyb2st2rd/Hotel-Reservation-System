from django import forms
from .models import Reservation
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from rooms.models import Chambre

class ReservationForm(forms.ModelForm):
    Email = forms.EmailField(required=False, label="Электронная почта")

    places = forms.ChoiceField(
        label="Количество мест",
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    Date_Check_In = forms.DateField(
        label="Дата заезда",
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )

    Date_Check_Out = forms.DateField(
        label="Дата выезда",
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )

    class Meta:
        model = Reservation
        fields = ['chambre', 'Name', 'Surname', 'Phone', 'Email', 'Date_Check_In', 'Date_Check_Out', 'places', 'Note']
        labels = {
            'chambre': _('Выберите номер'),
            'Name': _('Имя'),
            'Surname': _('Фамилия'),
            'Phone': _('Телефон'),
            'Email': _('Электронная почта'),
            'places': _('Место'),
            'Note': _('Комментарий'),
        }
        widgets = {
            'Note': forms.Textarea(attrs={'rows': 4}),
        }

    def get_booked_places(chambre, date_from, date_to):
        reservations = Reservation.objects.filter(
            chambre=chambre,
            Date_Check_Out__gt=date_from,
            Date_Check_In__lt=date_to
        )
        return sum(r.places for r in reservations)

    def is_room_available(chambre, date_from, date_to, requested_places):
        booked_places = get_booked_places(chambre, date_from, date_to)
        return chambre.capacity - booked_places >= requested_places

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        chambre_id = self.initial.get('chambre')
        if isinstance(chambre_id, Chambre):
            chambre_obj = chambre_id
        elif chambre_id:
            chambre_obj = Chambre.objects.filter(id=chambre_id).first()
        else:
            chambre_obj = None

        if chambre_obj:
            nom = chambre_obj.nom.lower()
            if 'муж' in nom:
                self.fields['places'].choices = [(str(i), str(i)) for i in range(1, 11)]
            elif 'жен' in nom:
                self.fields['places'].choices = [(str(i), str(i)) for i in range(1, 7)]
            else:
                self.fields.pop('places', None)

            self.fields['chambre'].initial = chambre_obj
            self.fields['chambre'].widget = forms.HiddenInput()
        else:
            self.fields.pop('places', None)

        if user and user.is_authenticated:
            self.fields.pop('Email', None)


class EditReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        exclude = ['user']
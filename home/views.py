from django.shortcuts import render
from .models import Testimonial
from django.shortcuts import render, redirect
from .forms import ReservationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Reservation
from .forms import EditReservationForm
from django.db import models
from django.db.models import Q
from django.contrib import messages
from rooms.models import Chambre
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from home.models import ActionLog

# Create your views here.


# Главная страница
def index(request):
    chambres = Chambre.objects.filter(disponibilité=True)
    testimonials = Testimonial.objects.all()
    show_login_reminder = not request.user.is_authenticated
    return render(request, "index.html", {
        'chambres': chambres,
        'testimonials': testimonials,
        'show_login_reminder': show_login_reminder
    })

# Бронирование
def reservation(request, room_id):
    chambre = get_object_or_404(Chambre, id=room_id)

    if request.method == "POST":
        form = ReservationForm(request.POST, user=request.user)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.chambre = chambre
            reservation.places = form.cleaned_data.get('places') or 1

            if not is_room_available(chambre, reservation.Date_Check_In, reservation.Date_Check_Out,
                                     reservation.places):
                messages.error(request, "Этот номер недоступен на выбранные даты. Попробуйте другой или смените даты.")
                return render(request, "reservation.html", {"form": form, "chambre": chambre})

            if request.user.is_authenticated:
                reservation.user = request.user
                reservation.Email = request.user.email

            reservation.save()
            messages.success(request, "Бронь успешно оформлена!")
            return redirect("dashboard")
    else:
        form = ReservationForm(initial={'chambre': chambre}, user=request.user)

    return render(request, "reservation.html", {"form": form, "chambre": chambre})

# Статичные страницы
def contact(request):
    return render(request, "contact.html")

def blog(request):
    chambres = Chambre.objects.all()
    return render(request, "blog.html", {'chambres': chambres})

def about(request):
    return render(request, 'about.html')

# Личный кабинет
@login_required
def dashboard(request):
    reservations = Reservation.objects.filter(
        Q(user=request.user) | Q(Email=request.user.email)
    )
    return render(request, "dashboard.html", {"reservations": reservations})

# Отмена бронирования
@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(
        Reservation,
        Q(pk=pk) & (Q(user=request.user) | Q(Email=request.user.email))
    )
    reservation.delete()

    ActionLog.objects.create(
        user=request.user,
        action="Отмена бронирования",
        description=f"Бронь #{reservation.id} отменена пользователем"
    )

    return redirect('dashboard')

# Редактирование брони
@login_required
def edit_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EditReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            return redirect('dashboard')

        ActionLog.objects.create(
            user=request.user,
            action="Редактирование бронирования",
            description=f"Бронь #{reservation.id} была отредактирована"
        )

    else:
        form = EditReservationForm(instance=reservation)
    return render(request, 'edit_reservation.html', {'form': form})

def get_booked_places(chambre, date_from, date_to):
    return Reservation.objects.filter(
        chambre=chambre,
        Date_Check_Out__gt=date_from,
        Date_Check_In__lt=date_to
    ).aggregate(total=Sum('places'))['total'] or 0

def is_room_available(chambre, date_from, date_to, requested_places=1):
    if chambre.nom.lower().startswith("муж") or chambre.nom.lower().startswith("жен"):
        booked = Reservation.objects.filter(
            chambre=chambre,
            Date_Check_Out__gt=date_from,
            Date_Check_In__lt=date_to
        ).aggregate(total=Sum('places'))['total'] or 0
        return chambre.capacity - booked >= requested_places
    else:
        return not Reservation.objects.filter(
            chambre=chambre,
            Date_Check_Out__gt=date_from,
            Date_Check_In__lt=date_to
        ).exists()

@login_required
def confirm_payment(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == 'POST':
        reservation.status = 'paid'
        reservation.save()

        # Подсчёт итоговой цены
        total_price = reservation.total_price() if hasattr(reservation, 'total_price') else reservation.chambre.prix

        # Логирование оплаты
        ActionLog.objects.create(
            user=request.user,
            action='Оплата бронирования',
            extra_data=f'Номер: {reservation.chambre.nom}, С {reservation.Date_Check_In} по {reservation.Date_Check_Out}, Сумма: {total_price} ₽'
        )

        # Отправка письма
        send_mail(
            subject='Подтверждение оплаты бронирования',
            message=(
                f'Здравствуйте, {reservation.Name} {reservation.Surname}!\n\n'
                f'Вы успешно оплатили бронирование номера "{reservation.chambre.nom}"\n'
                f'с {reservation.Date_Check_In} по {reservation.Date_Check_Out}.\n'
                f'Сумма к оплате: {total_price} ₽.\n\n'
                'Ждём Вас по адресу: ул. Свердлова 56\n\n'
                'Спасибо, что выбрали UHostel!'
                'Внимание: бронирование доступно только на сайте https://uhostel-ast.ru'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reservation.Email],
            fail_silently=False,
        )

        messages.success(request, 'Спасибо! Мы отправили вам письмо с подтверждением оплаты.')
    return redirect('dashboard')


def is_manager(user):
    return user.is_authenticated and user.role == 'manager'

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    return render(request, 'manager_dashboard.html')

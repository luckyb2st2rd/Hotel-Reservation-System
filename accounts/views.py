from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout as auth_logout
from .forms import EmailAuthenticationForm
from .forms import ChambreForm
from django.contrib.auth.decorators import user_passes_test
from home.models import Chambre
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from home.models import Reservation
import os
from django.conf import settings
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import random
from .models import Admin2FACode, CustomUser
from django.core.mail import send_mail
from home.models import ActionLog
from django.shortcuts import render
from django.http import HttpResponseForbidden

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            user_obj = None

        if user_obj is not None:
            user = authenticate(request, username=user_obj.username, password=password)
        else:
            user = None

        if user is not None:
            #Логирование после авторизации
            ActionLog.objects.create(
                user=user,
                action="Вход",
                description=f"{user.email} вошёл в систему"
            )

            if user.role == 'admin':
                code = str(random.randint(100000, 999999))
                Admin2FACode.objects.create(user=user, code=code)

                send_mail(
                    subject='Код подтверждения входа',
                    message=f'Ваш код подтверждения: {code}',
                    from_email='Uhostel-ast30@yandex.ru',
                    recipient_list=[user.email]
                )

                request.session['2fa_user_id'] = user.id
                return redirect('verify_2fa')
            else:
                login(request, user)
                return redirect('index')

        return render(request, 'login.html', {'error': 'Неверные данные'})

    return render(request, 'login.html')


def verify_2fa(request):
    if request.method == 'POST':
        input_code = request.POST.get('code')
        user_id = request.session.get('2fa_user_id')

        try:
            user = CustomUser.objects.get(id=user_id)
            code_entry = Admin2FACode.objects.filter(user=user).order_by('-created_at').first()
            if code_entry and not code_entry.is_expired() and code_entry.code == input_code:
                login(request, user)
                del request.session['2fa_user_id']
                return redirect('index')
            else:
                return render(request, 'verify_2fa.html', {'error': 'Неверный или просроченный код'})
        except CustomUser.DoesNotExist:
            return redirect('login')
    return render(request, 'verify_2fa.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

    ActionLog.objects.create(
        user=user,
        action="Регистрация",
        description=f"Зарегистрирован пользователь с email {user.email}"
    )

def logout(request):
    auth_logout(request)
    return redirect('index')

def manager_dashboard(request):
    rooms = Chambre.objects.all()
    if request.user.role != 'manager':
        return redirect('dashboard')
    return render(request, 'manager_dashboard.html', {'rooms': rooms})

def is_manager(user):
    return user.is_authenticated and user.role == 'manager'

@login_required
def edit_room(request, room_id):
    room = get_object_or_404(Chambre, id=room_id)
    if request.user.role != 'manager':
        return redirect('dashboard')

    if request.method == 'POST':
        form = ChambreForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = ChambreForm(instance=room)

    return render(request, 'edit_room.html', {'form': form})

@login_required
@user_passes_test(is_manager)
def add_room(request):
    if request.method == 'POST':
        form = ChambreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = ChambreForm()
    return render(request, 'room_form.html', {'form': form, 'title': 'Добавить номер'})

@login_required
@user_passes_test(is_manager)
def delete_room(request, pk):
    room = get_object_or_404(Chambre, pk=pk)
    room.delete()

    ActionLog.objects.create(
        user=request.user,
        action="Удаление номера",
        description=f"Номер '{room.nom}' был удалён"
    )

    return redirect('manager_dashboard')

# --- Генерация отчета через ReportLab ---

def generate_reservation_report(title, reservations):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{title}.pdf"'

    # Регистрируем кириллический шрифт
    font_path = os.path.join(settings.BASE_DIR, "static", "fonts", "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

    doc = SimpleDocTemplate(response, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'DejaVuSans'
    styles['Heading1'].fontName = 'DejaVuSans'
    styles['Heading1'].alignment = 1  # Центрировать

    elements = []
    elements.append(Paragraph(title, styles['Heading1']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Дата отчёта: {datetime.now().strftime('%d.%m.%Y')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Обработка данных по номерам
    chambre_data = {}
    for reservation in reservations:
        room = reservation.chambre
        if room.nom not in chambre_data:
            chambre_data[room.nom] = {'count': 0, 'total': 0}
        chambre_data[room.nom]['count'] += 1
        chambre_data[room.nom]['total'] += room.prix

    # Подготовка таблицы

    para_style = ParagraphStyle(name="TableCell", fontName="DejaVuSans", fontSize=10, leading=12)
    data = [["Дата", "Номер", "Кол-во броней", "Доход (₽)"]]

    for name, stats in chambre_data.items():
        data.append([
            datetime.now().strftime('%d.%m.%Y'),
            Paragraph(name, para_style),
            str(stats['count']),
            f"{stats['total']:.2f}"
        ])

    table = Table(data, colWidths=[40*mm, 80*mm, 35*mm, 30*mm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)
    doc.build(elements)
    return response

# --- Отчеты по периодам ---

def report_day(request):
    today = datetime.now().date()
    reservations = Reservation.objects.filter(Date_Check_In=today)
    return generate_reservation_report("Отчёт за день", reservations)

def report_week(request):
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    reservations = Reservation.objects.filter(Date_Check_In__range=(week_ago, today))
    return generate_reservation_report("Отчёт за неделю", reservations)

def report_month(request):
    today = datetime.now().date()
    month_ago = today - timedelta(days=30)
    reservations = Reservation.objects.filter(Date_Check_In__range=(month_ago, today))
    return generate_reservation_report("Отчёт за месяц", reservations)

def custom_lockout_response(request, credentials=None):
    return render(request, 'lockout.html', status=403)


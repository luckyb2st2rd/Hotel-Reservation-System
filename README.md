# 🏨 UHostel - Secure Web Application for Hostel Booking

[![Django](https://img.shields.io/badge/Django-3.0-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**Secure web application for the UHostel hostel booking system**

This project was developed as a **Bachelor's thesis** at Astrakhan State University, 
Faculty of Digital Technologies and Cybersecurity, Department of Information Security (2025).

---

## 📋 About

**Goal:** Develop a secure web application for automating room bookings with comprehensive information security measures.

## 👥 User Roles

| Role | Functions |
|------|-----------|
| 👤 **Client** | Registration, booking, SBP payment, booking history, profile |
| 📋 **Manager** | Room management, status updates, reports |
| ⚙️ **Admin** | User management, system settings, activity logs |

## 🔒 Security Features

| Threat | Protection |
|--------|------------|
| SQL Injection | Django ORM (automatic escaping) |
| CSRF | CSRF tokens (built-in) |
| Brute force | Django Axes (5 attempts → 10 min block) |
| 2FA for admins | Email OTP codes |
| MITM attacks | HTTPS + SSL |
| XSS | Automatic escaping, CSP headers |

## 🛠️ Tech Stack

**Backend:**
- Python 3.13 / Django 3.0
- SQLite (PostgreSQL ready)
- ReportLab (PDF reports)
- Django Axes (security)

**Frontend:**
- HTML5 / CSS3
- Bootstrap 5
- JavaScript

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/luckyb2st2rd/Hotel-Reservation-System.git
cd Hotel-Reservation-System

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

## 👨‍🎓 Author

**Artem Chigorov** (Чигаров Артем Александрович)

Bachelor's thesis, Information Systems and Technologies  
Security of Information Systems profile

*Astrakhan State University named after V.N. Tatishchev*  
*Astrakhan, 2025*

## 📜 License

MIT License - feel free to use for learning purposes

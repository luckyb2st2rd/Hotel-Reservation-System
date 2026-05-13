from django.shortcuts import render
from rooms.models import Chambre # Импорт модели из приложения rooms

def allRooms(request):
    chambres = Chambre.objects.all()
    return render(request, 'rooms.html', {'Chambres': chambres})
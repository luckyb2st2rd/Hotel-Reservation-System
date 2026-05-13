from django.contrib import admin
from rooms.models import Chambre

@admin.register(Chambre)
class ChambreAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prix', 'disponibilité')
    list_filter = ('disponibilité',)
    search_fields = ('nom',)
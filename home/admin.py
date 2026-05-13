from django.contrib import admin
from .models import Testimonial, Reservation
from rooms.models import Chambre
from .models import ActionLog

# Register your models here.
#admin.site.register(Chambre)
#admin.site.register(Catalogue)
admin.site.register(Testimonial)
admin.site.register(Reservation)
admin.site.register(ActionLog)
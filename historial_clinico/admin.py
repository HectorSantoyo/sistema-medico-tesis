from django.contrib import admin
from .models import RegistroClinico, Sintoma, Enfermedad

admin.site.register(RegistroClinico)
admin.site.register(Sintoma)
admin.site.register(Enfermedad)

from django.urls import path
from . import views

urlpatterns = [
    path('paciente/<int:paciente_id>/crear/', views.crear_registro_clinico, name='crear_registro_clinico'),
]

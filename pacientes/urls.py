# pacientes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('mis-pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('crear/', views.crear_paciente, name='crear_paciente'),
    path('<int:paciente_id>/editar/', views.editar_paciente, name='editar_paciente'),
    path('detalle/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),

]

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_medico, name='dashboard'),
    path('registrar/', views.registrar_medico, name='registrar_medico'),
]

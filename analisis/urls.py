from django.urls import path
from . import views

urlpatterns = [
    path('activas/', views.alertas_activas, name='alertas_activas'),
    path('<int:alerta_id>/resolver/', views.resolver_alerta, name='resolver_alerta'),
    path('dashboard/', views.dashboard_analisis, name='dashboard_analisis'),
]

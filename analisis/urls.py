from django.urls import path
from . import views

urlpatterns = [
    path('activas/', views.alertas_activas, name='alertas_activas'),
]

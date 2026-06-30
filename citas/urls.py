from django.urls import path
from . import views

urlpatterns = [
    path('proximas/', views.citas_proximas, name='citas_proximas'),
    path('crear/', views.crear_cita, name='crear_cita'),
    path('<int:cita_id>/editar/', views.editar_cita, name='editar_cita'),
    path('<int:cita_id>/eliminar/', views.eliminar_cita, name='eliminar_cita'),
]

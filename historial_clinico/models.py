from django.db import models
from pacientes.models import Paciente
from usuarios.models import Medico


class RegistroClinico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    diagnostico = models.TextField()
    tratamiento = models.TextField(blank=True)
    notas_adicionales = models.TextField(blank=True)

    def __str__(self):
        return f"{self.paciente} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

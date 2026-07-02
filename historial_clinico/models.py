from django.db import models
from pacientes.models import Paciente
from usuarios.models import Medico


class Sintoma(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Síntoma"
        verbose_name_plural = "Síntomas"

    def __str__(self):
        return self.nombre


class Enfermedad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    sintomas = models.ManyToManyField(Sintoma, related_name="enfermedades")

    class Meta:
        verbose_name = "Enfermedad"
        verbose_name_plural = "Enfermedades"

    def __str__(self):
        return self.nombre


class RegistroClinico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    diagnostico = models.TextField()
    tratamiento = models.TextField(blank=True)
    notas_adicionales = models.TextField(blank=True)
    sintomas = models.ManyToManyField(Sintoma, blank=True, related_name="registros_clinicos")

    def __str__(self):
        return f"{self.paciente} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

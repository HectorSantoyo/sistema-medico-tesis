from django.db import models
from usuarios.models import Medico  # Para relacionar pacientes con médicos


class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=10, choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino'), ('Otro', 'Otro')])
    telefono = models.CharField(max_length=15, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    antecedentes_medicos = models.TextField(blank=True)
    medico_asignado = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

from django.db import models
from pacientes.models import Paciente
from usuarios.models import Medico


class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=255, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('Agendada', 'Agendada'),
            ('Cancelada', 'Cancelada'),
            ('Reprogramada', 'Reprogramada'),
            ('Finalizada', 'Finalizada'),
        ],
        default='Agendada'
    )

    def __str__(self):
        return f"Cita de {self.paciente} con {self.medico} - {self.fecha} {self.hora}"

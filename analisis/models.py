from django.db import models
from pacientes.models import Paciente
from usuarios.models import Medico
from historial_clinico.models import Enfermedad

class AlertaClinica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)
    enfermedad = models.ForeignKey(Enfermedad, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_generada = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(help_text="Descripción breve del patrón detectado o posible riesgo.")
    nivel_riesgo = models.CharField(
        max_length=20,
        choices=[
            ('Bajo', 'Bajo'),
            ('Moderado', 'Moderado'),
            ('Alto', 'Alto'),
        ],
        default='Moderado'
    )
    resuelta = models.BooleanField(default=False, help_text="Marcar como resuelta una vez que el médico la revise.")

    def __str__(self):
        return f"Alerta para {self.paciente} - Riesgo: {self.nivel_riesgo}"

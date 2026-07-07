from django import forms
from .models import Cita
from pacientes.models import Paciente  # Asegúrate de importar esto

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        exclude = ['medico', 'estado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'motivo': forms.TextInput(attrs={'placeholder': 'Motivo de la consulta'}),
        }
        labels = {
            'paciente': 'Paciente',
            'fecha': 'Fecha',
            'hora': 'Hora',
            'motivo': 'Motivo',
        }

    def __init__(self, *args, **kwargs):
        medico = kwargs.pop('medico', None)  # Extrae el médico que le pasamos desde la vista
        super().__init__(*args, **kwargs)

        if medico:
            self.fields['paciente'].queryset = Paciente.objects.filter(medico_asignado=medico)

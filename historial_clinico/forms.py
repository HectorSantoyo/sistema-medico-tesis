from django import forms
from .models import RegistroClinico


class RegistroClinicoForm(forms.ModelForm):
    class Meta:
        model = RegistroClinico
        fields = ['diagnostico', 'tratamiento', 'notas_adicionales', 'sintomas']
        widgets = {
            'sintomas': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'diagnostico': 'Diagnóstico',
            'tratamiento': 'Tratamiento',
            'notas_adicionales': 'Notas adicionales',
            'sintomas': 'Síntomas',
        }

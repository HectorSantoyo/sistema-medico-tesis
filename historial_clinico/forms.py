from django import forms
from .models import RegistroClinico


class RegistroClinicoForm(forms.ModelForm):
    class Meta:
        model = RegistroClinico
        fields = ['diagnostico', 'tratamiento', 'notas_adicionales', 'sintomas']
        widgets = {
            'sintomas': forms.CheckboxSelectMultiple(),
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'rows': 2}),
            'notas_adicionales': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'diagnostico': 'Diagnóstico',
            'tratamiento': 'Tratamiento',
            'notas_adicionales': 'Notas adicionales',
            'sintomas': 'Síntomas',
        }

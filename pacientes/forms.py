from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        exclude = ['medico_asignado']

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono:
            raise forms.ValidationError('El número de teléfono es obligatorio.')
        if not telefono.isdigit():
            raise forms.ValidationError('El teléfono debe contener solo números.')
        if len(telefono) != 10:
            raise forms.ValidationError('El teléfono debe tener 10 dígitos.')
        return telefono

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if correo and not '@' in correo:
            raise forms.ValidationError('El correo debe tener un formato válido (contener "@").')
        return correo

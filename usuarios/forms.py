from django import forms
from django.contrib.auth.models import User
from usuarios.models import Medico

class RegistroMedicoForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = Medico
        fields = ['especialidad', 'telefono']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        medico = super().save(commit=False)
        medico.user = user
        if commit:
            medico.save()
        return medico

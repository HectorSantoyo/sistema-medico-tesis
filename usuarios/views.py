from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from usuarios.models import Medico
from pacientes.models import Paciente
from citas.models import Cita
from analisis.models import AlertaClinica
from datetime import date
from .forms import RegistroMedicoForm


@login_required
def dashboard_medico(request):
    medico = Medico.objects.get(user=request.user)

    total_pacientes = Paciente.objects.filter(medico_asignado=medico).count()
    citas_proximas = Cita.objects.filter(medico=medico, fecha__gte=date.today()).count()
    alertas_activas = AlertaClinica.objects.filter(medico=medico, resuelta=False).count()

    contexto = {
        'medico': medico,
        'total_pacientes': total_pacientes,
        'citas_proximas': citas_proximas,
        'alertas_activas': alertas_activas,
    }
    return render(request, 'usuarios/dashboard.html', contexto)

def registrar_medico(request):
    if request.method == 'POST':
        form = RegistroMedicoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroMedicoForm()
    return render(request, 'registro.html', {'form': form})
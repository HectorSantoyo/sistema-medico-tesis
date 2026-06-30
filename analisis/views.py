from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from analisis.models import AlertaClinica
from usuarios.models import Medico


@login_required
def alertas_activas(request):
    medico = Medico.objects.get(user=request.user)
    alertas = AlertaClinica.objects.filter(medico=medico, resuelta=False).order_by('-nivel_riesgo', '-fecha_generada')

    return render(request, 'analisis/alertas_activas.html', {'alertas': alertas})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from analisis.models import AlertaClinica
from usuarios.models import Medico


@login_required
def alertas_activas(request):
    medico = Medico.objects.get(user=request.user)
    alertas = AlertaClinica.objects.filter(medico=medico, resuelta=False).order_by('-nivel_riesgo', '-fecha_generada')

    return render(request, 'analisis/alertas_activas.html', {'alertas': alertas})


@login_required
def resolver_alerta(request, alerta_id):
    medico = Medico.objects.get(user=request.user)
    alerta = get_object_or_404(AlertaClinica, id=alerta_id, medico=medico)

    if request.method == 'POST':
        alerta.resuelta = True
        alerta.save()
        messages.success(request, 'Alerta marcada como resuelta.')

    return redirect('alertas_activas')

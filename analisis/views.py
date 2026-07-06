from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from analisis.models import AlertaClinica
from usuarios.models import Medico
from pacientes.models import Paciente
from historial_clinico.models import RegistroClinico


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


@login_required
def dashboard_analisis(request):
    medico = Medico.objects.get(user=request.user)

    total_pacientes = Paciente.objects.filter(medico_asignado=medico).count()
    total_registros_clinicos = RegistroClinico.objects.filter(medico=medico).count()

    alertas_medico = AlertaClinica.objects.filter(medico=medico)
    total_alertas = alertas_medico.count()
    alertas_activas = alertas_medico.filter(resuelta=False).count()
    alertas_resueltas = alertas_medico.filter(resuelta=True).count()

    niveles = ['Bajo', 'Moderado', 'Alto']
    conteo_por_nivel = {nivel: alertas_medico.filter(nivel_riesgo=nivel).count() for nivel in niveles}
    distribucion_por_nivel = [
        {
            'nivel': nivel,
            'total': conteo_por_nivel[nivel],
            'porcentaje': (conteo_por_nivel[nivel] / total_alertas * 100) if total_alertas else 0,
        }
        for nivel in niveles
    ]

    conteo_por_enfermedad = (
        alertas_medico.exclude(enfermedad=None)
        .values('enfermedad__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    distribucion_por_enfermedad = [
        {
            'enfermedad': fila['enfermedad__nombre'],
            'total': fila['total'],
            'porcentaje': (fila['total'] / total_alertas * 100) if total_alertas else 0,
        }
        for fila in conteo_por_enfermedad
    ]

    contexto = {
        'total_pacientes': total_pacientes,
        'total_registros_clinicos': total_registros_clinicos,
        'total_alertas': total_alertas,
        'alertas_activas': alertas_activas,
        'alertas_resueltas': alertas_resueltas,
        'distribucion_por_nivel': distribucion_por_nivel,
        'distribucion_por_enfermedad': distribucion_por_enfermedad,
    }
    return render(request, 'analisis/dashboard_analisis.html', contexto)

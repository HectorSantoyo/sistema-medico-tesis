from django.shortcuts import render, get_object_or_404, redirect
from pacientes.models import Paciente
from historial_clinico.models import RegistroClinico
from usuarios.models import Medico
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import PacienteForm
from django.contrib import messages


@login_required
def detalle_paciente(request, paciente_id):
    medico = Medico.objects.get(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, medico_asignado=medico)
    registros = RegistroClinico.objects.filter(paciente=paciente).order_by('-fecha')

    contexto = {
        'paciente': paciente,
        'registros': registros,
    }
    return render(request, 'pacientes/detalle_paciente.html', contexto)


@login_required
def lista_pacientes(request):
    medico = Medico.objects.get(user=request.user)
    pacientes = Paciente.objects.filter(medico_asignado=medico)

    return render(request, 'pacientes/lista_pacientes.html', {'pacientes': pacientes})


@login_required
def crear_paciente(request):
    medico = Medico.objects.get(user=request.user)

    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.medico_asignado = medico
            paciente.save()
            messages.success(request, 'Paciente ' + paciente.nombre + ' creado con éxito. ')
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()

    return render(request, 'pacientes/crear_paciente.html', {'form': form})


@login_required
def editar_paciente(request, paciente_id):
    medico = Medico.objects.get(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, medico_asignado=medico)

    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente ' + paciente.nombre + ' actualizado con éxito. ' )
            return redirect('lista_pacientes')
    else:
        form = PacienteForm(instance=paciente)

    return render(request, 'pacientes/editar_paciente.html', {'form': form, 'paciente': paciente})

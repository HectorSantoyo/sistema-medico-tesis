from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from citas.models import Cita
from usuarios.models import Medico
from datetime import date
from .forms import CitaForm
from django.contrib import messages


@login_required
def citas_proximas(request):
    medico = Medico.objects.get(user=request.user)
    citas = Cita.objects.filter(medico=medico, fecha__gte=date.today()).order_by('fecha', 'hora')

    return render(request, 'citas/citas_proximas.html', {'citas': citas})


@login_required
def crear_cita(request):
    medico = Medico.objects.get(user=request.user)

    if request.method == 'POST':
        form = CitaForm(request.POST, medico=medico)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.medico = medico
            cita.estado = 'Agendada'  # Valor por defecto
            cita.save()
            messages.success(request, 'Cita registrada con éxito. ' + cita.paciente.nombre + " " + str(cita.fecha))
            return redirect('citas_proximas')
    else:
        form = CitaForm(medico=medico)

    return render(request, 'citas/crear_cita.html', {'form': form})


@login_required
def editar_cita(request, cita_id):
    medico = Medico.objects.get(user=request.user)
    cita = get_object_or_404(Cita, id=cita_id, medico=medico)

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita, medico=medico)  # ✅ se pasa el médico
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita actualizada con éxito.')
            return redirect('citas_proximas')
    else:
        form = CitaForm(instance=cita, medico=medico)  # ✅ también aquí

    return render(request, 'citas/editar_cita.html', {'form': form, 'cita': cita})



@login_required
def eliminar_cita(request, cita_id):
    medico = Medico.objects.get(user=request.user)
    cita = get_object_or_404(Cita, id=cita_id, medico=medico)

    if request.method == 'POST':
        cita.delete()
        messages.success(request, 'Cita eliminada con éxito.')
        return redirect('citas_proximas')

    return render(request, 'citas/eliminar_cita.html', {'cita': cita})

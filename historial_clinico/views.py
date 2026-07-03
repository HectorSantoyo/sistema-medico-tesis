from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pacientes.models import Paciente
from usuarios.models import Medico
from .forms import RegistroClinicoForm


@login_required
def crear_registro_clinico(request, paciente_id):
    medico = Medico.objects.get(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, medico_asignado=medico)

    if request.method == 'POST':
        form = RegistroClinicoForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.paciente = paciente
            registro.medico = medico
            registro.save()
            form.save_m2m()
            messages.success(request, 'Registro clínico creado con éxito.')
            return redirect('detalle_paciente', paciente_id=paciente.id)
    else:
        form = RegistroClinicoForm()

    return render(request, 'historial_clinico/crear_registro.html', {'form': form, 'paciente': paciente})

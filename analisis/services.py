from historial_clinico.models import RegistroClinico, Enfermedad
from analisis.models import AlertaClinica

UMBRAL_MINIMO = 50
UMBRAL_MODERADO = 70
UMBRAL_ALTO = 85


def analizar_paciente_y_generar_alertas(paciente, medico):
    registros = RegistroClinico.objects.filter(paciente=paciente)

    sintomas_paciente = set()
    for registro in registros:
        sintomas_paciente.update(registro.sintomas.all())

    alertas_creadas = []

    for enfermedad in Enfermedad.objects.all():
        sintomas_enfermedad = set(enfermedad.sintomas.all())
        sintomas_totales_de_la_enfermedad = len(sintomas_enfermedad)

        if sintomas_totales_de_la_enfermedad == 0:
            continue

        sintomas_coincidentes = len(sintomas_paciente & sintomas_enfermedad)
        porcentaje = sintomas_coincidentes / sintomas_totales_de_la_enfermedad * 100

        if porcentaje < UMBRAL_MINIMO:
            continue

        if porcentaje >= UMBRAL_ALTO:
            nivel_riesgo = "Alto"
        elif porcentaje >= UMBRAL_MODERADO:
            nivel_riesgo = "Moderado"
        else:
            nivel_riesgo = "Bajo"

        ya_existe = AlertaClinica.objects.filter(
            paciente=paciente,
            medico=medico,
            enfermedad=enfermedad,
            resuelta=False,
        ).exists()

        if ya_existe:
            continue

        descripcion = (
            f"Alerta orientativa: el paciente presenta una coincidencia de "
            f"{porcentaje:.0f}% con los síntomas asociados a {enfermedad.nombre}. "
            "Esto no constituye un diagnóstico médico, es un apoyo para valoración "
            "clínica por parte del médico tratante."
        )

        alerta = AlertaClinica.objects.create(
            paciente=paciente,
            medico=medico,
            enfermedad=enfermedad,
            nivel_riesgo=nivel_riesgo,
            descripcion=descripcion,
        )
        alertas_creadas.append(alerta)

    return alertas_creadas

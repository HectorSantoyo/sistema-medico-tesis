from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from usuarios.models import Medico
from pacientes.models import Paciente
from historial_clinico.models import Sintoma, Enfermedad, RegistroClinico
from analisis.models import AlertaClinica
from analisis.services import analizar_paciente_y_generar_alertas

SINTOMAS_BASE = [
    "Sed excesiva",
    "Fatiga",
    "Visión borrosa",
    "Micción frecuente",
    "Dolor de cabeza",
    "Mareo",
    "Palpitaciones",
    "Palidez",
    "Debilidad",
    "Tos leve",
    "Dolor de garganta",
]

ENFERMEDADES_BASE = {
    "Diabetes": ["Sed excesiva", "Fatiga", "Visión borrosa", "Micción frecuente"],
    "Hipertensión": ["Dolor de cabeza", "Mareo", "Visión borrosa", "Palpitaciones"],
    "Anemia": ["Fatiga", "Palidez", "Mareo", "Debilidad"],
}

ESCENARIOS = [
    {
        "nombre": "Diabetes Sintetico",
        "nombre_paciente": "Diabetes",
        "apellido_paciente": "Sintetico",
        "sintomas": ["Sed excesiva", "Fatiga", "Visión borrosa", "Micción frecuente"],
        "esperado": "Diabetes: Alto",
    },
    {
        "nombre": "Hipertension Sintetico",
        "nombre_paciente": "Hipertension",
        "apellido_paciente": "Sintetico",
        "sintomas": ["Dolor de cabeza", "Mareo", "Visión borrosa"],
        "esperado": "Hipertensión: Moderado",
    },
    {
        "nombre": "Anemia Sintetico",
        "nombre_paciente": "Anemia",
        "apellido_paciente": "Sintetico",
        "sintomas": ["Fatiga", "Palidez", "Mareo"],
        "esperado": "Anemia: Moderado",
    },
    {
        "nombre": "Sin Alerta Sintetico",
        "nombre_paciente": "Sin Alerta",
        "apellido_paciente": "Sintetico",
        "sintomas": ["Tos leve", "Dolor de garganta"],
        "esperado": "Sin alertas",
    },
    {
        "nombre": "Mixto Sintetico",
        "nombre_paciente": "Mixto",
        "apellido_paciente": "Sintetico",
        "sintomas": ["Fatiga", "Mareo", "Visión borrosa"],
        "esperado": "Diabetes: Bajo, Hipertensión: Bajo, Anemia: Bajo",
    },
]


class Command(BaseCommand):
    help = "Carga datos sinteticos reproducibles para validar el motor de alertas (Sprint 4)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Borra los pacientes sinteticos del Sprint 4 (y sus registros/alertas) antes de recargar.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self._reset_datos_sinteticos()

        medico = self._crear_medico_sintetico()
        sintomas = self._crear_sintomas()
        enfermedades = self._crear_enfermedades(sintomas)
        pacientes_creados, pacientes_actualizados, pacientes_sinteticos = self._crear_escenarios(
            medico, sintomas
        )

        self._imprimir_resumen(
            pacientes_creados, pacientes_actualizados, enfermedades, pacientes_sinteticos
        )

    def _reset_datos_sinteticos(self):
        pacientes_sinteticos = Paciente.objects.filter(
            Q(nombre__icontains="Sintetico") | Q(apellido__icontains="Sintetico")
        )
        total = pacientes_sinteticos.count()
        # El borrado de Paciente hace CASCADE sobre RegistroClinico y AlertaClinica
        # (ambos declaran on_delete=CASCADE hacia Paciente), asi que no hace falta
        # borrarlos por separado.
        pacientes_sinteticos.delete()
        self.stdout.write(f"--reset: {total} paciente(s) sintetico(s) eliminados (con sus registros y alertas).")

    def _crear_medico_sintetico(self):
        user, user_creado = User.objects.get_or_create(
            username="medico_sintetico",
            defaults={
                "first_name": "Medico",
                "last_name": "Sintetico",
                "email": "medico_sintetico@example.com",
            },
        )
        if user_creado:
            user.set_password("sinteticotest123")
            user.save()

        medico, _ = Medico.objects.get_or_create(
            user=user,
            defaults={
                "especialidad": "Medicina General",
                "telefono": "0000000000",
            },
        )
        return medico

    def _crear_sintomas(self):
        sintomas = {}
        for nombre in SINTOMAS_BASE:
            sintoma, _ = Sintoma.objects.update_or_create(
                nombre=nombre,
                defaults={"descripcion": ""},
            )
            sintomas[nombre] = sintoma
        return sintomas

    def _crear_enfermedades(self, sintomas):
        enfermedades = {}
        for nombre, nombres_sintomas in ENFERMEDADES_BASE.items():
            enfermedad, _ = Enfermedad.objects.update_or_create(
                nombre=nombre,
                defaults={"descripcion": ""},
            )
            enfermedad.sintomas.set([sintomas[s] for s in nombres_sintomas])
            enfermedades[nombre] = enfermedad
        return enfermedades

    def _crear_escenarios(self, medico, sintomas):
        pacientes_creados = 0
        pacientes_actualizados = 0
        pacientes_sinteticos = []

        for escenario in ESCENARIOS:
            paciente, creado = Paciente.objects.get_or_create(
                nombre=escenario["nombre_paciente"],
                apellido=escenario["apellido_paciente"],
                medico_asignado=medico,
                defaults={
                    "edad": 40,
                    "sexo": "Otro",
                },
            )
            if creado:
                pacientes_creados += 1
            else:
                pacientes_actualizados += 1

            registro, _ = RegistroClinico.objects.get_or_create(
                paciente=paciente,
                medico=medico,
                diagnostico=f"Caso sintético Sprint 4 - {escenario['nombre']}",
                defaults={
                    "tratamiento": "No aplica, dato sintético",
                    "notas_adicionales": "Dato sintético Sprint 4",
                },
            )
            registro.sintomas.set([sintomas[s] for s in escenario["sintomas"]])

            with transaction.atomic():
                analizar_paciente_y_generar_alertas(paciente, medico)

            pacientes_sinteticos.append((escenario, paciente))

        return pacientes_creados, pacientes_actualizados, pacientes_sinteticos

    def _imprimir_resumen(self, pacientes_creados, pacientes_actualizados, enfermedades, pacientes_sinteticos):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Resumen de datos sinteticos (Sprint 4)"))
        self.stdout.write(f"Pacientes creados: {pacientes_creados}")
        self.stdout.write(f"Pacientes ya existentes (reutilizados): {pacientes_actualizados}")
        self.stdout.write(f"Enfermedades configuradas: {', '.join(enfermedades.keys())}")

        ids_pacientes = [paciente.id for _, paciente in pacientes_sinteticos]
        total_alertas = AlertaClinica.objects.filter(
            paciente_id__in=ids_pacientes, resuelta=False
        ).count()
        self.stdout.write(f"Alertas activas generadas para pacientes sinteticos: {total_alertas}")

        self.stdout.write("")
        self.stdout.write(f"{'Escenario':<25} | {'Esperado':<45} | Obtenido")
        self.stdout.write("-" * 100)
        for escenario, paciente in pacientes_sinteticos:
            alertas = AlertaClinica.objects.filter(paciente=paciente, resuelta=False).select_related("enfermedad")
            if alertas:
                obtenido = ", ".join(f"{a.enfermedad.nombre}: {a.nivel_riesgo}" for a in alertas)
            else:
                obtenido = "Sin alertas"
            self.stdout.write(f"{escenario['nombre']:<25} | {escenario['esperado']:<45} | {obtenido}")

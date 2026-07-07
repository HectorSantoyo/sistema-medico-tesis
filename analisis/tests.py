from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Medico
from pacientes.models import Paciente
from historial_clinico.models import Sintoma, Enfermedad, RegistroClinico
from analisis.models import AlertaClinica
from analisis.services import analizar_paciente_y_generar_alertas


class AlertEngineTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='medico1', password='pass12345')
        self.medico = Medico.objects.create(user=user, especialidad='Medicina General', telefono='111')
        self.paciente = Paciente.objects.create(
            nombre='Juan', apellido='Perez', edad=40, sexo='Masculino', medico_asignado=self.medico
        )

        nombres_sintomas = [
            'Sed excesiva', 'Fatiga', 'Visión borrosa', 'Micción frecuente',
            'Dolor de cabeza', 'Mareo', 'Palpitaciones', 'Palidez', 'Debilidad',
        ]
        self.sintomas = {nombre: Sintoma.objects.create(nombre=nombre) for nombre in nombres_sintomas}

        self.diabetes = Enfermedad.objects.create(nombre='Diabetes')
        self.diabetes.sintomas.set([
            self.sintomas['Sed excesiva'], self.sintomas['Fatiga'],
            self.sintomas['Visión borrosa'], self.sintomas['Micción frecuente'],
        ])

        self.hipertension = Enfermedad.objects.create(nombre='Hipertensión')
        self.hipertension.sintomas.set([
            self.sintomas['Dolor de cabeza'], self.sintomas['Mareo'],
            self.sintomas['Visión borrosa'], self.sintomas['Palpitaciones'],
        ])

        self.anemia = Enfermedad.objects.create(nombre='Anemia')
        self.anemia.sintomas.set([
            self.sintomas['Fatiga'], self.sintomas['Palidez'],
            self.sintomas['Mareo'], self.sintomas['Debilidad'],
        ])

    def _crear_registro(self, nombres_sintomas):
        registro = RegistroClinico.objects.create(
            paciente=self.paciente,
            medico=self.medico,
            diagnostico='Diagnóstico de prueba',
        )
        registro.sintomas.set([self.sintomas[nombre] for nombre in nombres_sintomas])
        return registro

    def test_genera_alerta_alto_con_coincidencia_completa(self):
        self._crear_registro(['Sed excesiva', 'Fatiga', 'Visión borrosa', 'Micción frecuente'])

        analizar_paciente_y_generar_alertas(self.paciente, self.medico)

        alerta = AlertaClinica.objects.get(paciente=self.paciente, enfermedad=self.diabetes)
        self.assertEqual(alerta.nivel_riesgo, 'Alto')

    def test_genera_alerta_moderado_con_tres_de_cuatro_sintomas(self):
        self._crear_registro(['Dolor de cabeza', 'Mareo', 'Visión borrosa'])

        analizar_paciente_y_generar_alertas(self.paciente, self.medico)

        alerta = AlertaClinica.objects.get(paciente=self.paciente, enfermedad=self.hipertension)
        self.assertEqual(alerta.nivel_riesgo, 'Moderado')

    def test_genera_alerta_bajo_con_dos_de_cuatro_sintomas(self):
        self._crear_registro(['Fatiga', 'Palidez'])

        analizar_paciente_y_generar_alertas(self.paciente, self.medico)

        alerta = AlertaClinica.objects.get(paciente=self.paciente, enfermedad=self.anemia)
        self.assertEqual(alerta.nivel_riesgo, 'Bajo')

    def test_no_genera_alerta_si_no_supera_umbral(self):
        self._crear_registro(['Fatiga'])

        analizar_paciente_y_generar_alertas(self.paciente, self.medico)

        self.assertFalse(AlertaClinica.objects.filter(paciente=self.paciente).exists())

    def test_no_duplica_alerta_activa(self):
        self._crear_registro(['Sed excesiva', 'Fatiga', 'Visión borrosa', 'Micción frecuente'])

        analizar_paciente_y_generar_alertas(self.paciente, self.medico)
        analizar_paciente_y_generar_alertas(self.paciente, self.medico)

        alertas = AlertaClinica.objects.filter(
            paciente=self.paciente, enfermedad=self.diabetes, resuelta=False
        )
        self.assertEqual(alertas.count(), 1)

    def test_usa_sintomas_acumulados_de_varios_registros(self):
        self._crear_registro(['Sed excesiva', 'Fatiga'])
        self._crear_registro(['Visión borrosa', 'Micción frecuente'])

        analizar_paciente_y_generar_alertas(self.paciente, self.medico)

        alerta = AlertaClinica.objects.get(paciente=self.paciente, enfermedad=self.diabetes)
        self.assertEqual(alerta.nivel_riesgo, 'Alto')


class AnalisisViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='medico1', password='pass12345')
        self.medico = Medico.objects.create(user=self.user, especialidad='Medicina General', telefono='111')
        self.paciente = Paciente.objects.create(
            nombre='Juan', apellido='Perez', edad=40, sexo='Masculino', medico_asignado=self.medico
        )
        self.enfermedad = Enfermedad.objects.create(nombre='Diabetes')
        self.alerta = AlertaClinica.objects.create(
            paciente=self.paciente,
            medico=self.medico,
            enfermedad=self.enfermedad,
            nivel_riesgo='Alto',
            descripcion='Alerta orientativa de prueba',
        )

        otro_user = User.objects.create_user(username='medico2', password='pass12345')
        self.otro_medico = Medico.objects.create(user=otro_user, especialidad='Medicina General', telefono='222')
        otro_paciente = Paciente.objects.create(
            nombre='Ana', apellido='Lopez', edad=35, sexo='Femenino', medico_asignado=self.otro_medico
        )
        self.alerta_otro_medico = AlertaClinica.objects.create(
            paciente=otro_paciente,
            medico=self.otro_medico,
            enfermedad=self.enfermedad,
            nivel_riesgo='Bajo',
            descripcion='Alerta orientativa de otro médico',
        )

    def test_alertas_activas_requiere_login(self):
        response = self.client.get(reverse('alertas_activas'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_alertas_activas_muestra_solo_alertas_del_medico(self):
        self.client.login(username='medico1', password='pass12345')

        response = self.client.get(reverse('alertas_activas'))

        self.assertEqual(response.status_code, 200)
        alertas = list(response.context['alertas'])
        self.assertIn(self.alerta, alertas)
        self.assertNotIn(self.alerta_otro_medico, alertas)

    def test_dashboard_analisis_responde_para_medico_autenticado(self):
        self.client.login(username='medico1', password='pass12345')

        response = self.client.get(reverse('dashboard_analisis'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_pacientes'], 1)
        self.assertEqual(response.context['alertas_activas'], 1)

    def test_resolver_alerta_marca_resuelta(self):
        self.client.login(username='medico1', password='pass12345')

        response = self.client.post(reverse('resolver_alerta', kwargs={'alerta_id': self.alerta.id}))

        self.assertRedirects(response, reverse('alertas_activas'))
        self.alerta.refresh_from_db()
        self.assertTrue(self.alerta.resuelta)

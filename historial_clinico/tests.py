from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Medico
from pacientes.models import Paciente
from historial_clinico.models import Sintoma, Enfermedad, RegistroClinico


class RegistroClinicoViewTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='medico1', password='pass12345')
        self.medico = Medico.objects.create(user=user, especialidad='Medicina General', telefono='111')
        self.paciente = Paciente.objects.create(
            nombre='Juan', apellido='Perez', edad=40, sexo='Masculino', medico_asignado=self.medico
        )

        otro_user = User.objects.create_user(username='medico2', password='pass12345')
        self.otro_medico = Medico.objects.create(user=otro_user, especialidad='Medicina General', telefono='222')
        self.paciente_ajeno = Paciente.objects.create(
            nombre='Ana', apellido='Lopez', edad=35, sexo='Femenino', medico_asignado=self.otro_medico
        )

        self.sintoma = Sintoma.objects.create(nombre='Fatiga')
        self.enfermedad = Enfermedad.objects.create(nombre='Anemia')
        self.enfermedad.sintomas.set([self.sintoma])

        self.url_paciente_propio = reverse('crear_registro_clinico', kwargs={'paciente_id': self.paciente.id})
        self.url_paciente_ajeno = reverse('crear_registro_clinico', kwargs={'paciente_id': self.paciente_ajeno.id})

    def test_crear_registro_clinico_requiere_login(self):
        response = self.client.get(self.url_paciente_propio)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_medico_puede_crear_registro_para_su_paciente(self):
        self.client.login(username='medico1', password='pass12345')

        response = self.client.post(self.url_paciente_propio, {
            'diagnostico': 'Diagnóstico de prueba',
            'tratamiento': 'Tratamiento de prueba',
            'notas_adicionales': 'Notas de prueba',
            'sintomas': [self.sintoma.id],
        })

        self.assertRedirects(
            response, reverse('detalle_paciente', kwargs={'paciente_id': self.paciente.id})
        )
        registro = RegistroClinico.objects.get(paciente=self.paciente)
        self.assertEqual(registro.medico, self.medico)
        self.assertEqual(registro.diagnostico, 'Diagnóstico de prueba')
        self.assertIn(self.sintoma, registro.sintomas.all())

    def test_medico_no_puede_crear_registro_para_paciente_ajeno(self):
        self.client.login(username='medico1', password='pass12345')

        response_get = self.client.get(self.url_paciente_ajeno)
        self.assertEqual(response_get.status_code, 404)

        response_post = self.client.post(self.url_paciente_ajeno, {
            'diagnostico': 'Diagnóstico de prueba',
            'tratamiento': '',
            'notas_adicionales': '',
            'sintomas': [self.sintoma.id],
        })
        self.assertEqual(response_post.status_code, 404)
        self.assertFalse(RegistroClinico.objects.filter(paciente=self.paciente_ajeno).exists())

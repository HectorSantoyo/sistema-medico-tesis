from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Medico


class LogoutTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='medico1', password='pass12345')
        Medico.objects.create(user=user, especialidad='Medicina General', telefono='111')
        self.client.login(username='medico1', password='pass12345')

    def test_logout_por_post_desloguea_y_redirige_a_login(self):
        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        response = self.client.get(reverse('dashboard'))
        self.assertNotEqual(response.status_code, 200)

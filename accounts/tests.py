import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login_page')
        self.otp_verify_url = reverse('accounts:otp_verify')
        self.employees_url = reverse('emp_management:employees')
        self.test_user = User.objects.create_user(
            email='testuser@gmail.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )

    def test_login_from_different_ip(self):
        # Set a last login IP that is different from the one in the request
        self.test_user.last_login_ip = '10.0.0.1'
        self.test_user.save()

        # Simulate a login from a new IP
        different_ip = '192.168.1.1'

        response = self.client.post(self.login_url, {
            'email': self.test_user.email,
            'password': 'password123',
        }, HTTP_REMOTE_ADDR=different_ip, follow=True)

        self.assertRedirects(response, self.otp_verify_url)

    def test_login_from_same_ip(self):
        # Set the last login IP to be the same as the one in the request
        same_ip = '192.168.1.100'
        self.test_user.last_login_ip = same_ip
        self.test_user.save()

        # Simulate a login from the same IP
        response = self.client.post(self.login_url, {
            'email': self.test_user.email,
            'password': 'password123',
        }, REMOTE_ADDR=same_ip, follow=True)

        self.assertRedirects(response, self.employees_url)
##PARA MATEST IF MAGREREDIRECT SA OTP PAGE IF DIFFERENT IP AND EMPLOYEES PAGE IF SAME IP
#run lang command na
# python manage.py test

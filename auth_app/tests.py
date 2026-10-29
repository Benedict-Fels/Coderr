from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationTests(APITestCase):
    url = '/api/registration/'

    def setUp(self):
        self.valid_data = {
            'username': 'max',
            'email': 'max@mail.de',
            'password': 'sicher123',
            'repeated_password': 'sicher123',
            'type': 'customer',
        }

    def test_registration_success(self):
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), {'token', 'username', 'email', 'user_id'})

        user = User.objects.get(username='max')
        self.assertEqual(response.data['user_id'], user.id)
        self.assertTrue(user.check_password('sicher123'))
        self.assertEqual(user.type, 'customer')
        self.assertEqual(response.data['token'], Token.objects.get(user=user).key)

    def test_password_mismatch_returns_400(self):
        self.valid_data['repeated_password'] = 'anders'
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='max').exists())

    def test_duplicate_email_returns_400(self):
        User.objects.create_user(username='other', email='max@mail.de', password='x')
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_type_returns_400(self):
        self.valid_data['type'] = 'admin'
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_type_returns_400(self):
        del self.valid_data['type']
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_email_returns_400(self):
        del self.valid_data['email']
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    url = '/api/login/'

    def setUp(self):
        self.user = User.objects.create_user(
            username='max', email='max@mail.de', password='sicher123', type='business')

    def test_login_success(self):
        response = self.client.post(
            self.url, {'username': 'max', 'password': 'sicher123'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), {'token', 'username', 'email', 'user_id'})
        self.assertEqual(response.data['user_id'], self.user.id)

    def test_login_twice_returns_same_token(self):
        data = {'username': 'max', 'password': 'sicher123'}
        first = self.client.post(self.url, data, format='json')
        second = self.client.post(self.url, data, format='json')

        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data['token'], second.data['token'])

    def test_wrong_password_returns_400(self):
        response = self.client.post(
            self.url, {'username': 'max', 'password': 'falsch'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_unknown_user_returns_400(self):
        response = self.client.post(
            self.url, {'username': 'gibtsnicht', 'password': 'sicher123'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

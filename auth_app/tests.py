from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()

AUTH_RESPONSE_KEYS = {'token', 'username', 'email', 'user_id'}


class RegistrationTests(APITestCase):
    """Tests for POST /api/registration/."""

    url = '/api/registration/'

    def setUp(self):
        """Prepare valid registration data."""
        self.valid_data = {
            'username': 'max',
            'email': 'max@mail.de',
            'password': 'sicher123',
            'repeated_password': 'sicher123',
            'type': 'customer',
        }

    def post(self):
        """Send the registration data to the endpoint."""
        return self.client.post(self.url, self.valid_data, format='json')

    def test_registration_success(self):
        """A valid request creates the user, its type and a token."""
        response = self.post()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), AUTH_RESPONSE_KEYS)
        user = User.objects.get(username='max')
        self.assertEqual(response.data['user_id'], user.id)
        self.assertTrue(user.check_password('sicher123'))
        self.assertEqual(user.type, 'customer')
        token = Token.objects.get(user=user)
        self.assertEqual(response.data['token'], token.key)

    def test_password_mismatch_returns_400(self):
        """Different passwords are rejected and no user is created."""
        self.valid_data['repeated_password'] = 'anders'
        response = self.post()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='max').exists())

    def test_duplicate_email_returns_400(self):
        """An email address can only be registered once."""
        User.objects.create_user(
            username='other', email='max@mail.de', password='x')
        response = self.post()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_type_returns_400(self):
        """Only customer and business are valid types."""
        self.valid_data['type'] = 'admin'
        response = self.post()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_type_returns_400(self):
        """The type is required on registration."""
        del self.valid_data['type']
        response = self.post()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_email_returns_400(self):
        """The email is required on registration."""
        del self.valid_data['email']
        response = self.post()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    """Tests for POST /api/login/."""

    url = '/api/login/'

    def setUp(self):
        """Create a user who can log in."""
        self.user = User.objects.create_user(
            username='max', email='max@mail.de', password='sicher123',
            type='business')

    def login(self, username='max', password='sicher123'):
        """Send the given credentials to the endpoint."""
        data = {'username': username, 'password': password}
        return self.client.post(self.url, data, format='json')

    def test_login_success(self):
        """Correct credentials return the token and user data."""
        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), AUTH_RESPONSE_KEYS)
        self.assertEqual(response.data['user_id'], self.user.id)

    def test_login_twice_returns_same_token(self):
        """A second login reuses the existing token."""
        first = self.login()
        second = self.login()

        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data['token'], second.data['token'])

    def test_wrong_password_returns_400(self):
        """A wrong password returns 400 without a token."""
        response = self.login(password='falsch')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_unknown_user_returns_400(self):
        """An unknown username returns 400."""
        response = self.login(username='gibtsnicht')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

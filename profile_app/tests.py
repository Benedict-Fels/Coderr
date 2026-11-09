from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

TEXT_FIELDS = [
    'first_name', 'last_name', 'location', 'tel', 'description',
    'working_hours',
]


class ProfileDetailTests(APITestCase):
    """Tests for GET and PATCH /api/profile/{pk}/."""

    def setUp(self):
        """Create a business user and a customer."""
        self.business = User.objects.create_user(
            username='biz', email='biz@mail.de', password='x',
            type='business')
        self.customer = User.objects.create_user(
            username='kunde', email='kunde@mail.de', password='x',
            type='customer')
        self.url = f'/api/profile/{self.business.id}/'

    def test_unauthenticated_returns_401(self):
        """Profiles are only visible to logged-in users."""
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_by_user_id(self):
        """The pk in the URL is the user id."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.business.id)
        self.assertEqual(response.data['username'], 'biz')
        self.assertEqual(response.data['email'], 'biz@mail.de')
        self.assertIn('created_at', response.data)

    def test_empty_fields_are_empty_strings(self):
        """Empty text fields are returned as '' instead of null."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)

        for field in TEXT_FIELDS:
            self.assertEqual(
                response.data[field], '', msg=f'{field} ist nicht leer')

    def test_unknown_profile_returns_404(self):
        """An unknown user id returns 404."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/profile/9999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_patch(self):
        """The owner can change profile and user fields."""
        self.client.force_authenticate(user=self.business)
        data = {
            'location': 'Stuttgart',
            'first_name': 'Max',
            'email': 'neu@mail.de',
        }
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.business.refresh_from_db()
        self.assertEqual(self.business.location, 'Stuttgart')
        self.assertEqual(self.business.first_name, 'Max')
        self.assertEqual(self.business.email, 'neu@mail.de')

    def test_patch_with_taken_email_returns_400(self):
        """The email of another user cannot be taken over."""
        self.client.force_authenticate(user=self.business)
        data = {'email': 'kunde@mail.de'}
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_user_cannot_patch(self):
        """Only the owner may change a profile."""
        self.client.force_authenticate(user=self.customer)
        data = {'location': 'Hackerhausen'}
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.business.refresh_from_db()
        self.assertEqual(self.business.location, '')

    def test_type_cannot_be_changed(self):
        """The read-only type is ignored instead of raising an error."""
        self.client.force_authenticate(user=self.business)
        data = {'type': 'customer'}
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.business.refresh_from_db()
        self.assertEqual(self.business.type, 'business')


class ProfileListTests(APITestCase):
    """Tests for the business and customer profile lists."""

    def setUp(self):
        """Create one user of each type and log in as the customer."""
        User.objects.create_user(
            username='biz', password='x', type='business')
        self.customer = User.objects.create_user(
            username='kunde', password='x', type='customer')
        self.client.force_authenticate(user=self.customer)

    def test_business_list_contains_only_business(self):
        """The business list only contains business users."""
        response = self.client.get('/api/profiles/business/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'business')
        self.assertIn('working_hours', response.data[0])

    def test_customer_list_contains_only_customers(self):
        """The customer list only contains customers."""
        response = self.client.get('/api/profiles/customer/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'customer')
        self.assertIn('uploaded_at', response.data[0])
        self.assertNotIn('location', response.data[0])

    def test_lists_require_authentication(self):
        """Both lists are only visible to logged-in users."""
        self.client.force_authenticate(user=None)
        for url in ['/api/profiles/business/', '/api/profiles/customer/']:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED)

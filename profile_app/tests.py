from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from profile_app.models import Profile


class ProfileDetailTests(APITestCase):

    def setUp(self):
        # Zuerst ein User OHNE Profil, damit User-ID und Profil-ID auseinanderlaufen
        User.objects.create_user(username='admin', password='x')

        self.business = User.objects.create_user(
            username='biz', email='biz@mail.de', password='x')
        self.business_profile = Profile.objects.create(user=self.business, type='business')

        self.customer = User.objects.create_user(
            username='kunde', email='kunde@mail.de', password='x')
        Profile.objects.create(user=self.customer, type='customer')

        self.url = f'/api/profile/{self.business.id}/'

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_by_user_id(self):
        self.assertNotEqual(self.business.id, self.business_profile.id)  # die Falle ist aktiv

        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.business.id)
        self.assertEqual(response.data['username'], 'biz')
        self.assertEqual(response.data['email'], 'biz@mail.de')

    def test_empty_fields_are_empty_strings(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)

        for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
            self.assertEqual(response.data[field], '', msg=f'{field} ist nicht leer')

    def test_unknown_profile_returns_404(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/profile/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_patch(self):
        self.client.force_authenticate(user=self.business)
        data = {'location': 'Stuttgart', 'first_name': 'Max', 'email': 'neu@mail.de'}
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.business.refresh_from_db()
        self.business_profile.refresh_from_db()
        self.assertEqual(self.business_profile.location, 'Stuttgart')
        self.assertEqual(self.business.first_name, 'Max')
        self.assertEqual(self.business.email, 'neu@mail.de')

    def test_other_user_cannot_patch(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(self.url, {'location': 'Hackerhausen'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.business_profile.refresh_from_db()
        self.assertEqual(self.business_profile.location, '')

    def test_type_cannot_be_changed(self):
        self.client.force_authenticate(user=self.business)
        self.client.patch(self.url, {'type': 'customer'}, format='json')

        self.business_profile.refresh_from_db()
        self.assertEqual(self.business_profile.type, 'business')


class ProfileListTests(APITestCase):

    def setUp(self):
        business = User.objects.create_user(username='biz', password='x')
        Profile.objects.create(user=business, type='business')

        self.customer = User.objects.create_user(username='kunde', password='x')
        Profile.objects.create(user=self.customer, type='customer')

        self.client.force_authenticate(user=self.customer)

    def test_business_list_contains_only_business(self):
        response = self.client.get('/api/profiles/business/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'business')
        self.assertIn('working_hours', response.data[0])

    def test_customer_list_contains_only_customers(self):
        response = self.client.get('/api/profiles/customer/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'customer')
        self.assertIn('uploaded_at', response.data[0])
        self.assertNotIn('location', response.data[0])

    def test_lists_require_authentication(self):
        self.client.force_authenticate(user=None)
        for url in ['/api/profiles/business/', '/api/profiles/customer/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

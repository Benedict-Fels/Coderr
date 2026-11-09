from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail

User = get_user_model()


def make_detail(offer_type, price):
    """Build the request data for one offer detail."""
    return {
        'title': f'{offer_type.title()} Design',
        'revisions': 2,
        'delivery_time_in_days': 5,
        'price': price,
        'features': ['Logo Design', 'Visitenkarte'],
        'offer_type': offer_type,
    }


class OfferCreateTests(APITestCase):
    """Tests for POST /api/offers/."""

    url = '/api/offers/'

    def setUp(self):
        self.business = User.objects.create_user(username='biz', password='x', type='business')
        self.customer = User.objects.create_user(username='kunde', password='x', type='customer')

        self.valid_data = {
            'title': 'Grafikdesign-Paket',
            'image': None,
            'description': 'Ein umfassendes Paket.',
            'details': [
                make_detail('basic', 100),
                make_detail('standard', 200),
                make_detail('premium', 500),
            ],
        }

    def test_business_can_create_offer(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data.keys()), {'id', 'title', 'image', 'description', 'details'})
        self.assertEqual(len(response.data['details']), 3)
        self.assertIn('id', response.data['details'][0])
        self.assertEqual(response.data['details'][0]['price'], 100)

        offer = Offer.objects.get(id=response.data['id'])
        self.assertEqual(offer.user, self.business)
        self.assertEqual(offer.details.count(), 3)

    def test_user_in_body_is_ignored(self):
        self.client.force_authenticate(user=self.business)
        self.valid_data['user'] = self.customer.id
        response = self.client.post(self.url, self.valid_data, format='json')

        offer = Offer.objects.get(id=response.data['id'])
        self.assertEqual(offer.user, self.business)

    def test_unauthenticated_returns_401(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_returns_403(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Offer.objects.count(), 0)

    def test_two_details_returns_400(self):
        self.client.force_authenticate(user=self.business)
        self.valid_data['details'].pop()
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Offer.objects.count(), 0)

    def test_duplicate_offer_type_returns_400(self):
        self.client.force_authenticate(user=self.business)
        self.valid_data['details'][2]['offer_type'] = 'basic'
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_detail_returns_400(self):
        self.client.force_authenticate(user=self.business)
        del self.valid_data['details'][1]['price']
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferDetail.objects.count(), 0)

    def test_missing_title_returns_400(self):
        self.client.force_authenticate(user=self.business)
        del self.valid_data['title']
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

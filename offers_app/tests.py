from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail

User = get_user_model()

OFFER_RESPONSE_KEYS = {'id', 'title', 'image', 'description', 'details'}


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
        """Create a business user, a customer and valid offer data."""
        self.business = User.objects.create_user(
            username='biz', password='x', type='business')
        self.customer = User.objects.create_user(
            username='kunde', password='x', type='customer')
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

    def post_as(self, user):
        """Send the offer data as the given user."""
        self.client.force_authenticate(user=user)
        return self.client.post(self.url, self.valid_data, format='json')

    def test_business_can_create_offer(self):
        """A business user creates an offer with three details."""
        response = self.post_as(self.business)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), OFFER_RESPONSE_KEYS)
        self.assertEqual(len(response.data['details']), 3)
        self.assertIn('id', response.data['details'][0])
        self.assertEqual(response.data['details'][0]['price'], 100)
        offer = Offer.objects.get(id=response.data['id'])
        self.assertEqual(offer.user, self.business)
        self.assertEqual(offer.details.count(), 3)

    def test_user_in_body_is_ignored(self):
        """The creator is always the logged-in user."""
        self.valid_data['user'] = self.customer.id
        response = self.post_as(self.business)

        offer = Offer.objects.get(id=response.data['id'])
        self.assertEqual(offer.user, self.business)

    def test_unauthenticated_returns_401(self):
        """Anonymous users cannot create offers."""
        response = self.post_as(None)

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_returns_403(self):
        """Customers cannot create offers."""
        response = self.post_as(self.customer)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Offer.objects.count(), 0)

    def test_two_details_returns_400(self):
        """An offer needs exactly three details."""
        self.valid_data['details'].pop()
        response = self.post_as(self.business)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Offer.objects.count(), 0)

    def test_duplicate_offer_type_returns_400(self):
        """Each offer type must appear exactly once."""
        self.valid_data['details'][2]['offer_type'] = 'basic'
        response = self.post_as(self.business)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_detail_returns_400(self):
        """A detail without price is rejected before anything is saved."""
        del self.valid_data['details'][1]['price']
        response = self.post_as(self.business)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferDetail.objects.count(), 0)

    def test_missing_title_returns_400(self):
        """The title is required."""
        del self.valid_data['title']
        response = self.post_as(self.business)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

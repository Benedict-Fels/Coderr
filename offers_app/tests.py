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


def create_offer(user, title, prices, delivery_times):
    """Create an offer with a basic, standard and premium detail."""
    offer = Offer.objects.create(
        user=user, title=title, description=f'{title} Beschreibung')
    offer_types = ['basic', 'standard', 'premium']
    for offer_type, price, days in zip(offer_types, prices, delivery_times):
        OfferDetail.objects.create(
            offer=offer, title=offer_type, revisions=1,
            delivery_time_in_days=days, price=price, offer_type=offer_type)
    return offer


class OfferListTests(APITestCase):
    """Tests for GET /api/offers/."""

    url = '/api/offers/'

    def setUp(self):
        """Create two business users with offers of different prices."""
        self.anna = User.objects.create_user(
            username='anna', password='x', type='business',
            first_name='Anna', last_name='Muster')
        self.ben = User.objects.create_user(
            username='ben', password='x', type='business')
        self.logo = create_offer(
            self.anna, 'Logo Design', [500, 100, 300], [7, 3, 10])
        self.web = create_offer(
            self.ben, 'Website', [50, 200, 400], [14, 21, 30])

    def get_results(self, query=''):
        """Request the list and return the results of the first page."""
        response = self.client.get(self.url + query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['results']

    def titles(self, query=''):
        """Return the titles of the listed offers in their order."""
        return [offer['title'] for offer in self.get_results(query)]

    def test_list_is_public_and_paginated(self):
        """Anonymous users get a paginated list."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {'count', 'next', 'previous', 'results'})
        self.assertEqual(response.data['count'], 2)

    def test_min_values_are_computed_from_details(self):
        """min_price and min_delivery_time are the lowest detail values."""
        results = self.get_results(f'?creator_id={self.anna.id}')
        logo = results[0]

        self.assertEqual(logo['min_price'], 100)
        self.assertEqual(logo['min_delivery_time'], 3)

    def test_list_contains_user_details_and_detail_links(self):
        """Each offer shows its creator and links to its details."""
        logo = self.get_results(f'?creator_id={self.anna.id}')[0]

        self.assertEqual(
            logo['user_details'],
            {'first_name': 'Anna', 'last_name': 'Muster',
             'username': 'anna'})
        self.assertEqual(len(logo['details']), 3)
        first = logo['details'][0]
        self.assertEqual(set(first.keys()), {'id', 'url'})
        self.assertIn(f'/api/offerdetails/{first["id"]}/', first['url'])

    def test_filter_by_creator(self):
        """creator_id only returns offers of that user."""
        self.assertEqual(
            self.titles(f'?creator_id={self.ben.id}'), ['Website'])

    def test_filter_by_min_price(self):
        """min_price excludes offers whose cheapest detail is cheaper."""
        self.assertEqual(self.titles('?min_price=80'), ['Logo Design'])

    def test_filter_by_max_delivery_time(self):
        """max_delivery_time keeps offers deliverable within that time."""
        self.assertEqual(
            self.titles('?max_delivery_time=5'), ['Logo Design'])

    def test_ordering_by_min_price(self):
        """Offers can be sorted by their minimum price in both directions."""
        self.assertEqual(
            self.titles('?ordering=min_price'), ['Website', 'Logo Design'])
        self.assertEqual(
            self.titles('?ordering=-min_price'), ['Logo Design', 'Website'])

    def test_search_in_title_and_description(self):
        """search looks into title and description."""
        self.assertEqual(self.titles('?search=logo'), ['Logo Design'])
        self.assertEqual(self.titles('?search=beschreibung'), [
            'Website', 'Logo Design'])

    def test_page_size(self):
        """page_size limits the number of results per page."""
        response = self.client.get(self.url + '?page_size=1')

        self.assertEqual(len(response.data['results']), 1)
        self.assertIsNotNone(response.data['next'])

    def test_invalid_filter_returns_400(self):
        """A non-numeric filter value is rejected."""
        response = self.client.get(self.url + '?min_price=abc')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OfferDetailRetrieveTests(APITestCase):
    """Tests for GET /api/offerdetails/{id}/."""

    def setUp(self):
        """Create an offer and remember its basic detail."""
        self.user = User.objects.create_user(
            username='biz', password='x', type='business')
        offer = create_offer(self.user, 'Logo', [100, 200, 300], [1, 2, 3])
        self.detail = offer.details.get(offer_type='basic')
        self.url = f'/api/offerdetails/{self.detail.id}/'

    def test_returns_full_detail(self):
        """Logged-in users get all fields of the detail."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['offer_type'], 'basic')
        self.assertEqual(response.data['price'], 100)

    def test_unauthenticated_returns_401(self):
        """Offer details are only visible to logged-in users."""
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unknown_detail_returns_404(self):
        """An unknown id returns 404."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/offerdetails/9999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

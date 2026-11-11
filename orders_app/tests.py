from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order

User = get_user_model()


def create_users():
    """Create a business user, a second business user and a customer."""
    business = User.objects.create_user(
        username='biz', password='x', type='business')
    other_business = User.objects.create_user(
        username='biz2', password='x', type='business')
    customer = User.objects.create_user(
        username='kunde', password='x', type='customer')
    return business, other_business, customer


def create_detail(business):
    """Create an offer of the business user and return its basic detail."""
    offer = Offer.objects.create(user=business, title='Logo')
    return OfferDetail.objects.create(
        offer=offer, title='Logo Basic', revisions=3,
        delivery_time_in_days=5, price=150,
        features=['Logo Design', 'Visitenkarte'], offer_type='basic')


def create_order(customer, business, order_status='in_progress'):
    """Create an order between the two users directly in the database."""
    return Order.objects.create(
        customer_user=customer, business_user=business, title='Logo',
        revisions=1, delivery_time_in_days=5, price=100,
        offer_type='basic', status=order_status)


class OrderCreateTests(APITestCase):
    """Tests for POST /api/orders/."""

    url = '/api/orders/'

    def setUp(self):
        """Create the users and an offer detail to order."""
        self.business, _, self.customer = create_users()
        self.detail = create_detail(self.business)

    def post_as(self, user, data):
        """Send the order data as the given user."""
        self.client.force_authenticate(user=user)
        return self.client.post(self.url, data, format='json')

    def test_customer_can_order(self):
        """The order copies the detail and links both users."""
        data = {'offer_detail_id': self.detail.id}
        response = self.post_as(self.customer, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_user'], self.customer.id)
        self.assertEqual(response.data['business_user'], self.business.id)
        self.assertEqual(response.data['title'], 'Logo Basic')
        self.assertEqual(response.data['price'], 150)
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertNotIn('offer_detail_id', response.data)

    def test_order_keeps_price_after_offer_changes(self):
        """A later price change does not affect existing orders."""
        response = self.post_as(
            self.customer, {'offer_detail_id': self.detail.id})
        self.detail.price = 999
        self.detail.save()

        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.price, 150)

    def test_business_cannot_order(self):
        """Only customers may create orders."""
        data = {'offer_detail_id': self.detail.id}
        response = self.post_as(self.business, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 0)

    def test_unauthenticated_returns_401(self):
        """Anonymous users cannot order."""
        data = {'offer_detail_id': self.detail.id}
        response = self.post_as(None, data)

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_offer_detail_id_returns_400(self):
        """The offer_detail_id is required."""
        response = self.post_as(self.customer, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_offer_detail_id_returns_400(self):
        """The offer_detail_id must be a number."""
        response = self.post_as(self.customer, {'offer_detail_id': 'abc'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_offer_detail_returns_404(self):
        """An unknown offer detail returns 404."""
        response = self.post_as(self.customer, {'offer_detail_id': 9999})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderListTests(APITestCase):
    """Tests for GET /api/orders/."""

    url = '/api/orders/'

    def setUp(self):
        """Create one order of the business user and one of another."""
        self.business, self.other, self.customer = create_users()
        self.own = create_order(self.customer, self.business)
        self.foreign = create_order(self.customer, self.other)

    def ids_for(self, user):
        """Return the ids of the orders visible to the given user."""
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return {order['id'] for order in response.data}

    def test_customer_sees_all_own_orders(self):
        """The customer sees the orders with both business users."""
        self.assertEqual(
            self.ids_for(self.customer), {self.own.id, self.foreign.id})

    def test_business_sees_only_own_orders(self):
        """A business user only sees orders where it is the provider."""
        self.assertEqual(self.ids_for(self.business), {self.own.id})

    def test_unauthenticated_returns_401(self):
        """Orders are only visible to logged-in users."""
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderUpdateDestroyTests(APITestCase):
    """Tests for PATCH and DELETE /api/orders/{id}/."""

    def setUp(self):
        """Create an order and an admin."""
        self.business, self.other, self.customer = create_users()
        self.order = create_order(self.customer, self.business)
        self.admin = User.objects.create_user(
            username='admin', password='x', is_staff=True)
        self.url = f'/api/orders/{self.order.id}/'

    def patch_as(self, user, data):
        """Send a PATCH request with the given data as the given user."""
        self.client.force_authenticate(user=user)
        return self.client.patch(self.url, data, format='json')

    def delete_as(self, user):
        """Send a DELETE request as the given user."""
        self.client.force_authenticate(user=user)
        return self.client.delete(self.url)

    def test_business_user_can_update_status(self):
        """The order's business user can change the status."""
        response = self.patch_as(self.business, {'status': 'completed'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

    def test_invalid_status_returns_400(self):
        """Only the defined status values are allowed."""
        response = self.patch_as(self.business, {'status': 'fertig'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_fields_return_400(self):
        """Fields other than status are rejected."""
        data = {'status': 'completed', 'price': 1}
        response = self.patch_as(self.business, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_progress')

    def test_customer_cannot_update(self):
        """The customer of the order cannot change the status."""
        response = self.patch_as(self.customer, {'status': 'completed'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_business_cannot_update(self):
        """Another business user cannot change the status."""
        response = self.patch_as(self.other, {'status': 'completed'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_order_returns_404(self):
        """An unknown order returns 404."""
        self.client.force_authenticate(user=self.business)
        response = self.client.patch(
            '/api/orders/9999/', {'status': 'completed'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_delete(self):
        """Admins can delete orders."""
        response = self.delete_as(self.admin)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_business_user_cannot_delete(self):
        """Not even the order's business user may delete it."""
        response = self.delete_as(self.business)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Order.objects.filter(id=self.order.id).exists())

    def test_delete_unauthenticated_returns_401(self):
        """Anonymous users cannot delete orders."""
        response = self.delete_as(None)

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderCountTests(APITestCase):
    """Tests for the order-count and completed-order-count endpoints."""

    def setUp(self):
        """Create two running and one completed order of the business."""
        self.business, _, self.customer = create_users()
        create_order(self.customer, self.business)
        create_order(self.customer, self.business)
        create_order(self.customer, self.business, 'completed')
        create_order(self.customer, self.business, 'cancelled')
        self.client.force_authenticate(user=self.customer)

    def test_order_count(self):
        """Only orders in progress are counted."""
        response = self.client.get(f'/api/order-count/{self.business.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'order_count': 2})

    def test_completed_order_count(self):
        """Only completed orders are counted."""
        url = f'/api/completed-order-count/{self.business.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'completed_order_count': 1})

    def test_customer_id_returns_404(self):
        """Only business users can be counted."""
        response = self.client.get(f'/api/order-count/{self.customer.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unknown_user_returns_404(self):
        """An unknown user id returns 404."""
        response = self.client.get('/api/completed-order-count/9999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        """Counts are only visible to logged-in users."""
        self.client.force_authenticate(user=None)
        response = self.client.get(f'/api/order-count/{self.business.id}/')

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED)

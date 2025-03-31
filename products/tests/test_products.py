from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from products.models import Category, Product, Review

User = get_user_model()

class ProductTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@example.com', 
            password='adminpass'
        )
        self.user = User.objects.create_user(
            email='user@example.com',
            password='userpass'
        )
        self.category = Category.objects.create(name='Electronics', description='Gadgets')
        self.product = Product.objects.create(
            title='Smartphone',
            description='Flagship device',
            price=999.99,
            category=self.category,
            stock=10
        )

    def test_product_list(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_product_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'title': 'Laptop',
            'description': 'Powerful laptop',
            'price': 1999.99,
            'category': self.category.slug,
            'stock': 5
        }
        response = self.client.post(reverse('product-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_review(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'content': 'Отличный товар!',
            'rating': 5
        }
        
        url = reverse('review-list', kwargs={'product_pk': self.product.pk})
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from unittest.mock import patch
from users.tokens import account_activation_token

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.valid_user = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'username': 'testuser',
            'phone': '+1234567890',
            'address': 'Test Address'
        }

    @patch('users.serializers.send_mail')
    def test_register_user(self, mock_send_mail):
        """Test user registration with valid data."""
        response = self.client.post(self.register_url, self.valid_user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, self.valid_user['email'])
        self.assertFalse(user.is_active)

        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        self.assertEqual(args[3], [self.valid_user['email']])
        self.assertIn('Активация аккаунта', args[0])

    def test_register_user_with_existing_email(self):
        """Test registration with an existing email."""
        User.objects.create_user(**self.valid_user)
        response = self.client.post(self.register_url, self.valid_user)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_weak_password(self):
        """Test registration with a weak password."""
        data = {**self.valid_user, 'password': '123'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_succesfuly_activation(self):
        """Test account activation."""
        user = User.objects.create_user(**self.valid_user, is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        response = self.client.get(
            reverse('activate', kwargs={'uidb64': uid, 'token': token})
        )
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Аккаунт активирован!')

    def test_invalid_activation_token(self):
        """Test invalid token"""
        user = User.objects.create_user(**self.valid_user, is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user) + 'invalid'
        response = self.client.get(
            reverse('activate', kwargs={'uidb64': uid, 'token': token})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_login_with_email(self):
        """Test login with email"""
        User.objects.create_user(**self.valid_user, is_active=True)
        response = self.client.post(self.login_url, {
            'email': self.valid_user['email'],
            'password': self.valid_user['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_with_username(self):
        """Test login with username"""
        User.objects.create_user(**self.valid_user, is_active=True)
        response = self.client.post(self.login_url, {
            'username': self.valid_user['username'],
            'password': self.valid_user['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_login_inactive_account(self):
        User.objects.create_user(**self.valid_user, is_active= False)
        response = self.client.post(self.login_url, {
            'email': self.valid_user['email'],
            'password': self.valid_user['password']
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_login_invalid_credentials(self):
        User.objects.create_user(**self.valid_user, is_active=True)
        response = self.client.post(self.login_url, {
            'email': self.valid_user['email'],
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)




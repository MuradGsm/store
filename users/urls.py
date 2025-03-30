from django.urls import path
from users.views import RegisterView, LoginView, ActivateAccountView




urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('activate/<str:uidb64>/<str:token>/', ActivateAccountView.as_view(), name='activate'),
]
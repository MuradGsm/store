from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import CategoryViewSet, ProductViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'products/(?P<product_pk>\d+)/reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import VisitViewSet

router = DefaultRouter()
router.register(r'visits', VisitViewSet, basename='visit')

urlpatterns = [
    path('', include(router.urls)),
]

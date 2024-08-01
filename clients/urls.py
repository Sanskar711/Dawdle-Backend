from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ProductViewSet, UseCaseViewSet, ProspectViewSet, MeetingViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'products', ProductViewSet)
router.register(r'usecases', UseCaseViewSet)
router.register(r'prospects', ProspectViewSet)
router.register(r'meetings', MeetingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

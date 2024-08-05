from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ProductViewSet, UseCaseViewSet, ProspectViewSet, MeetingViewSet, UserProductsView,AssignedProductsView

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'products', ProductViewSet)
router.register(r'usecases', UseCaseViewSet)
router.register(r'prospects', ProspectViewSet)
router.register(r'meetings', MeetingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user-products/', UserProductsView.as_view(), name='user-products'),
    path('products/<int:pk>/usecases/', ProductViewSet.as_view({'get': 'usecases'}), name='product-usecases'),
    path('products/<int:pk>/add-usecase/', ProductViewSet.as_view({'post': 'add_usecase'}), name='add-product-usecase'),
    path('products/<int:pk>/prospects/', ProductViewSet.as_view({'get': 'prospects'}), name='product-prospects'),
    path('products/<int:pk>/add-prospect/', ProductViewSet.as_view({'post': 'add_prospect'}), name='add-product-prospect'),
    path('<int:pk>/company-info/', ClientViewSet.as_view({'get': 'company_info'}), name='client-company-info'),
    path('assigned-products/', AssignedProductsView.as_view(), name='assigned-products'),  # Add this line
]

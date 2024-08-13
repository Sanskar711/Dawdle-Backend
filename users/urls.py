from django.urls import path,include
from . import views
# from django.contrib import auth
urlpatterns = [
    path('register/', views.register, name='register'),
    path('signin/', views.signin, name='signin'),
    path('verify_otp_login/<int:user_id>/', views.verify_otp_login, name='verify_otp_login'),
    path('home/', views.home, name='home'),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('session/',views.session_view, name='session'),
    # path('logout/', views.logout_view,name='logout'),
    # path('profile/', views.UserProfileDetail.as_view(), name='api_profile'),
    # path('debug_session/',views.debug_session_view,name='debugsession')
    path('<int:user_id>/profile/',views.UserProfileDetail.as_view(),name='profile_view'),
    path('logout/', views.UserLogoutView.as_view(), name='logout_view'),
    path('verification-status/',views.UserVerificationStatusView.as_view(),name='verification-status'),
    path('user-products/', views.UserProductsView.as_view(), name='user-products'),
    path('product/<int:product_id>/info/', views.ProductInfoView.as_view(), name='product-info'),
    path('product/<int:product_id>/prospects/', views.ProductProspectsView.as_view(), name='product-prospects'),
    path('product/<int:product_id>/usecases/', views.ProductUseCasesView.as_view(), name='product-usecases'),
    path('product/<int:product_id>/usecases/<int:usecase_id>/', views.UseCaseDetailView.as_view(), name='usecase-details'),
]

from django.urls import path
from .views import register, login_view, verify_otp, verify_otp_login, home, DashboardView

urlpatterns = [
    path('register/', register, name='register'),
    path('verify_otp/<int:user_id>/', verify_otp, name='verify_otp'),
    path('verify_otp_login/<int:user_id>/', verify_otp_login, name='verify_otp_login'),
    path('login/', login_view, name='login'),
    path('home/', home, name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]

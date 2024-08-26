from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('signin/', views.signin, name='signin'),
    path('verify_otp_login/<int:user_id>/', views.verify_otp_login, name='verify_otp_login'),
    # path('home/', views.home, name='home'),
    # path('public/csrf-token/', views.csrf_token_view, name='csrf-token'),
   
    # path('logout/', views.user_logout_view, name='logout_view'),
    path('<int:user_id>/update-profile/', views.user_profile_detail, name='update-profile'),
    path('<int:user_id>/profile/', views.user_profile_detail, name='fetch-profile'),
    path('verification-status/', views.user_verification_status_view, name='verification-status'),
    path('user-products/', views.user_products_view, name='user-products'),
    path('product/<int:product_id>/info/', views.product_info_view, name='product-info'),
    path('prospect/<int:prospect_id>/info/', views.prospect_info_view, name='prospect-info'),
    path('product/<int:product_id>/prospects/', views.product_prospects_view, name='product-prospects'),
    path('product/<int:product_id>/usecases/', views.product_use_cases_view, name='product-usecases'),
    path('product/<int:product_id>/usecases/<int:usecase_id>/', views.use_case_detail_view, name='usecase-details'),
    path('product/<int:product_id>/questions/', views.product_questions_view, name='product-questions'),
    path('prospects/create/', views.create_prospect, name='prospect-create'),
    path('meetings/create/', views.create_meeting, name='create-meeting'),
    path('meetings/', views.user_meetings_api, name='user-meetings'),
    path('products/<int:product_id>/add_prospect/<int:prospect_id>/', views.add_prospect_to_product, name='add_prospect_to_product'),
    path('meetings/<int:meeting_id>/', views.meeting_detail, name='meeting_detail'),
    path('email-request/', views.send_email_request, name='send_email_request'),
]

from django.urls import path
from . import views
from .views import (
    client_product_list, client_product_detail,
    client_usecase_list, client_usecase_detail,
    client_prospect_list, client_prospect_detail,
    client_resource_list, client_resource_detail,
    client_qualifying_question_list, client_qualifying_question_detail,
    client_ideal_customer_profile_list, client_ideal_customer_profile_detail,
    client_meeting_list, client_meeting_detail
)




urlpatterns = [
    
    path('signin/', views.signin_client, name='signin_client'),
    path('verify_otp_login/<int:client_id>/', views.verify_client_otp_login, name='verify_otp_login'), 
    path('client-info/',views.client_info,name='client-info'),
    path('client/update/', views.update_client_info, name='update_client_info'),
    path('products/', client_product_list, name='client-product-list'),
    path('products/<int:pk>/', client_product_detail, name='client-product-detail'),

    path('products/<int:product_id>/use-cases/', client_usecase_list, name='client-usecase-list'),
    path('products/<int:product_id>/use-cases/<int:pk>/', client_usecase_detail, name='client-usecase-detail'),
    path('products/<int:product_id>/use-cases/add/', client_usecase_list, name='client-usecase-add'),
    path('products/<int:product_id>/use-cases/<int:pk>/update/', client_usecase_detail, name='client-usecase-update'),

    path('products/<int:product_id>/prospects/', client_prospect_list, name='client-prospect-list'),
    path('products/<int:product_id>/prospects/<int:pk>/', client_prospect_detail, name='client-prospect-detail'),

    path('products/<int:product_id>/resources/', client_resource_list, name='client-resource-list'),
    path('products/<int:product_id>/resources/<int:pk>/', client_resource_detail, name='client-resource-detail'),

    path('products/<int:product_id>/qualifying-questions/', client_qualifying_question_list, name='client-qualifying-question-list'),
    path('products/<int:product_id>/qualifying-questions/<int:pk>/', client_qualifying_question_detail, name='client-qualifying-question-detail'),

    path('products/<int:product_id>/ideal-customer-profiles/', client_ideal_customer_profile_list, name='client-ideal-customer-profile-list'),
    path('products/<int:product_id>/ideal-customer-profiles/<int:pk>/', client_ideal_customer_profile_detail, name='client-ideal-customer-profile-detail'),

    path('products/<int:product_id>/meetings/', client_meeting_list, name='client-meeting-list'),
    path('products/<int:product_id>/meetings/<int:pk>/', client_meeting_detail, name='client-meeting-detail'),
    path('meetings/', views.entire_client_meeting_list, name='client-meeting-list'),
    path('meetings/<int:meeting_id>/', views.meeting_detail, name='meeting-detail'),
    path('prospects/<int:prospect_id>/', views.prospect_detail, name='prospect-detail'),
    path('use-cases/<int:usecase_id>/', views.usecase_detail, name='usecase-detail'),
    path('qualifying-questions/<int:question_id>/', views.qualifying_question_detail, name='qualifyingquestion-detail'),
    
    

]

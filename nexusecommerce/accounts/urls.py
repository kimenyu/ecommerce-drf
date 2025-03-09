from django.urls import path
from .views import LoginView, RegisterCustomerView, RegisterAdminView

urlpatterns = [
    path('register-customer/', RegisterCustomerView.as_view(), name='register-customer'),
    path('register-admin/', RegisterAdminView.as_view(), name='register-admin'),
    path('login-user/', LoginView.as_view(), name='login-user')
]
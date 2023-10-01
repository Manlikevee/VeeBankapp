from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_view
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import *
from .serializer import *

router = DefaultRouter()

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('sample/', SampleAPI.as_view(), name='sample-api'),
    path('userprofile/', userprofile, name='sample-userprofile'),
    path('transactions/', transactions, name='sample-transactions'),
    path('/bank/resolve/<str:id>', get_account_details, name='get_account_details'),


]

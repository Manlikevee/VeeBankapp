from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Customize the token data here
        token['username'] = user.username
        token['email'] = user.email

        return token



class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'id']  # Or specify the fields you want to expose



class Completeprofile(serializers.ModelSerializer):
    user = Userserializer()

    class Meta:
        model = Profile
        fields = '__all__'  # Or specify the fields you want to expose
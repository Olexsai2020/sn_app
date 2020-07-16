from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import Post, Like


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserSignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        user = get_user_model().objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password is not found'
            )
        try:
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, user)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        return {'email': user.email,
                'token': jwt_token}


class UserActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('last_login', 'last_activity')


class PostSerializer(serializers.ModelSerializer):
    user = serializers.CharField(max_length=255,
                                 default=serializers.CurrentUserDefault())

    class Meta:
        model = Post
        fields = ('id', 'title', 'body_text', 'likes_count', 'user')


class AnalyticsSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='created_at__date')
    likes = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('date', 'likes')

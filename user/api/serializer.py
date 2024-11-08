import datetime

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "password2",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"error": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):

        user_name = validated_data["username"]
        user_name = user_name.lower()
        user = User.objects.create(
            username=user_name,
        )
        user.set_password(validated_data["password"])
        user.save()

        return user


class LoginSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["user_id"] = str(user.id)
        return token

    def handel_error(self, error):
        print(error)
        if isinstance(error.detail, list) and len(error.detail) == 1:
            error.detail = error.detail[0]
        elif isinstance(error.detail, str):
            pass
            # error_response.data = get_response(
            #     message=error[0], status_code=error_response.status_code)
        elif isinstance(error, dict):
            pass
        raise error

    def validate(self, attrs):
        username = attrs.get("username")
        if username:
            username = username.lower()
        data = {}

        user = User.objects.get(username=username)
        user.save()
        attrs["username"] = user.username
        data = super(LoginSerializer, self).validate(attrs)
        user_serializer = UserSerializer(user)
        data.update({"user_data": user_serializer.data})
        return data

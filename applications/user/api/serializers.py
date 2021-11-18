import os
from rest_framework import serializers
from rest_framework.utils import model_meta
from applications.user.models import *
from django.contrib.auth import authenticate, password_validation
from drf_writable_nested.mixins import (
    UniqueFieldsMixin,
    NestedUpdateMixin,
    NestedCreateMixin,
)

from drf_writable_nested.serializers import WritableNestedModelSerializer


class PasswordResetSerializer(serializers.Serializer):
    username = serializers.CharField(label="Username", write_only=True, required=True)
    password = serializers.CharField(
        label="Password",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=True,
    )
    password1 = serializers.CharField(
        label="Password1",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=True,
    )
    password2 = serializers.CharField(
        label="Password2",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=True,
    )

    def validate_password1(self, password1):
        password_validation.validate_password(password1, self.instance)
        return password1

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")
        if password1 != password2:
            error = {
                "password1": [
                    "Las contraseñas no coinciden",
                ],
                "password2": [
                    "Las contraseñas no coinciden",
                ],
            }
            raise serializers.ValidationError(error)

        user = authenticate(
            required=self.context.get("request"), username=username, password=password
        )

        if not user:
            error = {
                "password": [
                    "Su contraseña antigua es incorrecta",
                ]
            }
            raise serializers.ValidationError(error, code="authotization")
        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data.get("user")
        user.set_password(self.validated_data.get("password"))
        user.save()
        return user


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"

    def update(self, instance, validated_data):
        if instance.picture:
            if os.path.isfile(instance.picture.path) and validated_data.get("picture"):
                os.remove(instance.picture.path)

        return super().update(instance, validated_data)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ("is_superuser", "groups", "user_permissions", "date_joined")
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}}
        }


class CompanySerializer(serializers.ModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = CompanyUser
        fields = "__all__"


class AccountUpdateSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            "id",
            "username",
            "is_active",
            "last_login",
            "type",
        )
        read_only_fields = (
            "id",
            "is_active",
            "last_login",
            "type",
        )


class CompanyUpdateSerializer(NestedUpdateMixin, serializers.ModelSerializer):
    account = AccountUpdateSerializer()

    class Meta:
        model = CompanyUser
        fields = "__all__"

    def update(self, instance, validated_data):
        if instance.logo:
            if os.path.isfile(instance.logo.path) and validated_data.get("logo"):
                os.remove(instance.logo.path)

        return super().update(instance, validated_data)


class EmployeUpdateSerializer(NestedUpdateMixin, serializers.ModelSerializer):
    account = AccountUpdateSerializer()
    person = PersonSerializer()
    company = CompanyUpdateSerializer(read_only=True)

    class Meta:
        model = EmployeUser
        fields = "__all__"


class AccountSignupSerializer(UniqueFieldsMixin, serializers.ModelSerializer):

    password2 = serializers.CharField(
        label="Confirmación",
        style={"input_type": "password"},
        max_length=150,
        write_only=True,
    )

    class Meta:
        model = Account
        fields = (
            "id",
            "username",
            "password",
            "password2",
            "is_active",
            "last_login",
            "type",
        )

        read_only_fields = ("id", "is_active", "last_login", "type")
        write_only_fields = ("password",)

    def validate_password(self, password):
        password_validation.validate_password(password, self.instance)
        return password

    def validate(self, data):
        if data["password"] != data["password2"]:
            error = {
                "password": [
                    "Las contraseñas no coinciden",
                ],
                "password2": [
                    "Las contraseñas no coinciden",
                ],
            }
            raise serializers.ValidationError(error)
        return data

    def create(self, validated_data):
        self._validate_unique_fields(validated_data)
        del validated_data["password2"]
        account = super(UniqueFieldsMixin, self).create(validated_data)
        account.set_password(validated_data["password"])
        account.save()
        return account

    def update(self, instace, validated_data):
        self._validate_unique_fields(validated_data)
        account = super().update(instace, validated_data)
        account.set_password(validated_data["password"])
        account.save()
        return account


class CompanySignupSerializer(NestedCreateMixin, serializers.ModelSerializer):

    account = AccountSignupSerializer()

    def create(self, validated_data):
        company = super().create(validated_data)
        account = company.account
        account.type = Account.Types.Company
        account.save()
        return company

    class Meta:
        model = CompanyUser
        fields = "__all__"


class EmployeSerializer(
    NestedUpdateMixin, NestedCreateMixin, serializers.ModelSerializer
):
    account = AccountSignupSerializer()
    person = PersonSerializer()
    company = CompanySerializer(read_only=True)

    class Meta:
        model = EmployeUser
        fields = "__all__"
        # depth = 2

    def create(self, validated_data):
        company = self.context["user"].get_company()
        validated_data["company_id"] = company.id
        employe = super().create(validated_data)
        account = employe.account
        account.type = Account.Types.Employe
        account.save()
        return employe

# import time
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from applications.user.models import Account
from rest_framework.generics import UpdateAPIView, CreateAPIView, RetrieveUpdateAPIView
from django.contrib.auth import login, logout
from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .serializers import *
from .mixins import AuthticationMixin


class UserLoginApiView(ObtainAuthToken):
    """vista para hacer el login del usuario"""

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        if user.type == Account.Types.Company:
            cuenta = CompanySerializer(
                user.get_companyuser(), context={"request": request}
            ).data
        else:
            cuenta = EmployeSerializer(
                user.get_companyuser(), context={"request": request}
            ).data

        return Response(
            {
                "token": token.key,
                "user": cuenta,
            },
            status.HTTP_200_OK,
        )


class PasswordResetApiView(APIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({})


class CheckTokenApiView(AuthticationMixin, APIView):
    """vista para verificar el token"""

    def post(self, request, *args, **kwargs):
        token = self.token
        user = token.user
        # time.sleep(10)

        if user.type == Account.Types.Company:
            cuenta = CompanySerializer(
                user.get_companyuser(), context={"request": request}
            ).data
        else:
            cuenta = EmployeSerializer(
                user.get_companyuser(), context={"request": request}
            ).data
        return Response({"token": token.key, "user": cuenta})


class UserLogoutApiView(AuthticationMixin, APIView):
    """vista para cerrar cesion del usuario"""

    def post(self, request, *args, **kwargs):
        self.token.delete()
        logout(self.request)
        return Response({"message": "Sesión cerrada con éxito"}, status.HTTP_200_OK)


class CompanyUserSignupApiView(CreateAPIView):
    """vista para registrar empresas"""

    serializer_class = CompanySignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        company = serializer.save()

        token, created = Token.objects.get_or_create(user=company.account)
        login(request, user=company.account)

        return Response(
            {
                "token": token.key,
                "user": serializer.data,
            },
            status.HTTP_201_CREATED,
        )


class EmployeUserViewset(AuthticationMixin, viewsets.ModelViewSet):
    """vista que maneja crud de empleados"""

    serializer_class = EmployeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "person__first_name",
        "person__last_name",
        "person__email",
    ]

    def get_queryset(self):
        company = self.token.user.get_company()
        queryset = EmployeUser.objects.filter(company=company)
        return queryset

    def get_serializer(self, *args, **kwargs):
        serializer = self.get_serializer_class()
        context = self.get_serializer_context()
        context["user"] = self.token.user
        kwargs["context"] = context
        return serializer(*args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        employe = self.get_object()
        account = employe.account
        person = employe.person
        account.delete()
        person.delete()
        employe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompanyUserProfileUpdateApiview(AuthticationMixin, UpdateAPIView):
    serializer_class = CompanyUpdateSerializer
    queryset = CompanyUser.objects.all()


class EmployeUserProfileUpdateApiview(UpdateAPIView):

    serializer_class = EmployeUpdateSerializer
    queryset = EmployeUser.objects.all()


class TestApiView(viewsets.ModelViewSet):
    """vista para hacer pruebas"""

    serializer_class = CompanySignupSerializer
    queryset = CompanyUser.objects.all()

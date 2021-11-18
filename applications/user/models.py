import os
from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey, OneToOneField
from applications.user.managers import CustomUserManager
from .managers import CustomUserManager


class Person(models.Model):
    GENDER_CHOICES = (
        ("M", "Masculino"),
        ("F", "Femenino"),
        ("O", "Otro"),
    )

    first_name = models.CharField("Nombres", max_length=150)
    last_name = models.CharField("Apellidos", max_length=150)
    email = models.EmailField("Email", blank=True, null=True)
    phone = models.CharField("Telefono", max_length=12, blank=True, null=True)
    address = models.CharField("dirección", max_length=150, blank=True, null=True)
    birth = models.DateField(
        "Fecha de nacimiento", auto_now=False, auto_now_add=False, blank=True, null=True
    )
    gender = models.CharField("Genero", max_length=1, choices=GENDER_CHOICES)
    picture = models.ImageField(
        "Foto de perfil", upload_to="profile", max_length=256, blank=True, null=True
    )

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.picture.path):
            os.remove(self.picture.path)
        return super().delete(*args, **kwargs)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        verbose_name = "persona"
        verbose_name_plural = "personas"


class Account(AbstractUser, PermissionsMixin):
    class Types(models.TextChoices):
        Company = "COMPANY", "COMPANY"
        Employe = "EMPLOYE", "EMPLOYE"

    first_name = "none"
    last_name = "none"
    email = "none"
    is_superuser = models.BooleanField("superusuario", default=False)
    type = models.CharField(
        "Tipo de usuario", max_length=10, blank=False, choices=Types.choices
    )
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def get_companyuser(self):
        if self.type == str(Account.Types.Company):
            return self.companyuser
        if self.type == str(Account.Types.Employe):
            return self.employeuser
        return None

    def get_company(self):
        if self.type == str(Account.Types.Company):
            return self.companyuser
        if self.type == str(Account.Types.Employe):
            return self.employeuser.company
        return None

    class Meta:
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"


class CompanyUser(models.Model):
    account = OneToOneField(
        Account, verbose_name="Cuenta", on_delete=CASCADE, null=False
    )
    name = models.CharField(
        "Nombre de la empresa", max_length=50, null=False, unique=True
    )
    phone = models.CharField("Telefono", max_length=50, blank=True, null=True)
    logo = models.ImageField(
        "logo", upload_to="logo", max_length=256, blank=True, null=True
    )

    address = models.CharField("Dirección", max_length=50, blank=True, null=True)

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.logo.path):
            os.remove(self.logo.path)
        return super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.name


class EmployeUser(models.Model):
    CHOICES_ROL = (
        ("Administrador", "Administrador"),
        ("Cajero", "Cajero"),
        ("Almacén", "Almacén"),
        ("Ninguno", "Ninguno"),
    )
    account = OneToOneField(
        Account, verbose_name="Cuenta", on_delete=CASCADE, null=False, blank=False
    )
    person = OneToOneField(
        Person,
        verbose_name="Datos personales",
        on_delete=CASCADE,
        blank=False,
        null=False,
    )
    company = ForeignKey(CompanyUser, on_delete=CASCADE, verbose_name="Empresa")
    rol = models.CharField("Rol", max_length=20, blank=False, choices=CHOICES_ROL)

    def __str__(self):
        return str(self.person)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"


class Client(models.Model):
    person = OneToOneField(
        Person,
        verbose_name="Datos personales",
        on_delete=CASCADE,
        blank=False,
        null=False,
    )

    def __str__(self):
        return str(self.person)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

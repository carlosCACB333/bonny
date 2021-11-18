from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def _create_user(
        self, username, password, is_staff, is_superuser, is_active, **extra_fields
    ):
        if not username:
            raise ValueError(("El usuario es requerido"))
        if not password:
            raise ValueError(("La contraseña es requerido"))
        user = self.model(
            username=username,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        return self._create_user(username, password, False, False, True, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        return self._create_user(username, password, True, True, True, **extra_fields)

from datetime import timedelta
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone
from django.conf import settings


class UserTokenAuthentication(TokenAuthentication):
    def expire_in(self, token):
        time_elapsed = timezone.now()-token.created
        left_time = timedelta(
            seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS)-time_elapsed
        return left_time

    def is_token_expired(self, token):
        return self.expire_in(token) < timedelta(seconds=0)

    def authenticate_credentials(self, key):
        token, is_valid, message = None, False, None

        try:
            token = self.get_model().objects.select_related('user').get(key=key)
            is_valid = True
        except:
            message = 'Token inválido'

        if token:
            if not token.user.is_active:
                message = 'Usuario elimiando o Inactivo'
                is_valid = False
                token.delete()
            if self.is_token_expired(token):
                message = 'El token a expirado'
                is_valid = False
                token.delete()

        return (token, message, is_valid)

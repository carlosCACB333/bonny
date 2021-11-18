
from rest_framework.authentication import get_authorization_header
from .Autentications import UserTokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer


class AuthticationMixin(object):
    token = None

    def get_user(self, request):
        header = get_authorization_header(request).split()
        try:
            reques_token = header[1].decode()
        except:
            return None, 'No se envió el token de autenticacion', False
        token, message, is_valid = UserTokenAuthentication(
        ).authenticate_credentials(reques_token)
        return(token, message, is_valid)

    def dispatch(self, request, *args, **kwargs):
        token, message, is_valid = self.get_user(request)
        if is_valid:
            self.token = token
            return super().dispatch(request, *args, **kwargs)
        else:
            response = Response({'permitted': False, message: message},
                                status.HTTP_401_UNAUTHORIZED)
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = 'application/json'
            response.renderer_context = {}
            return response

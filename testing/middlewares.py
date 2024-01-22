import jwt
from django.contrib.auth.backends import BaseBackend
from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework import exceptions

from users.models import User

client_secret = "VU3CvpMhFVUq1gqkjEylFXR638zsIDU0"
ALGORITHM = "RS256"


class KeyCloakAuth(BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request, username=None, password=None):
        decoded = self._decode_jwt(request.headers.get("Authorization"))
        if not decoded:
            return None, None
        username = decoded.get('preferred_username')
        if not username:
            raise exceptions.MethodNotAllowed('Invalid token')
        user = User.objects.filter(username=username).first()
        return user, None

    def _decode_jwt(self, token):
        try:
            token = str.replace(token, 'Bearer ', '')

            return jwt.decode(
                jwt=token,
                key=client_secret,
                algorithms=[ALGORITHM],
                options={"verify_signature": False}
            )
        except Exception as e:
            return None


class KeycloakAuthenticationScheme(SimpleJWTScheme):
    target_class = KeyCloakAuth
    name = 'BearerToken'
    priority = -1
    match_subclasses = True

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name='Authorization',
            token_prefix=self.target.keyword,
        )

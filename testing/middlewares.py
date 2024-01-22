"""
Custom JWT Authentication Module for Django Rest Framework
with Keycloak Integration.
This module enables seamless integration between Django Rest Framework (DRF)
andKeycloak for JSON Web Token (JWT) based user authentication.
Users are authenticated using JWT tokens issued by Keycloak,
and the module provides flexibility in
configuration for easy adaptation to different Keycloak setups.
"""
import jwt
from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

from users.models import User

CLIENT_SECRET = "VU3CvpMhFVUq1gqkjEylFXR638zsIDU0"
ALGORITHM = "RS256"


class KeyCloakAuth(BaseAuthentication):
    """
       The class of authorization module that
       inherits from the BaseAuthentication module
    """
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
                key=CLIENT_SECRET,
                algorithms=[ALGORITHM],
                options={"verify_signature": False}
            )
        except Exception:
            return None


class KeycloakAuthenticationScheme(SimpleJWTScheme):
    """
        An authorization module class that creates
        an authorization scheme for drf_spectacular
    """
    target_class = KeyCloakAuth
    name = 'BearerToken'
    priority = -1
    match_subclasses = True

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name='Authorization',
            token_prefix=self.target.keyword,
        )

from typing import Tuple, TYPE_CHECKING
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

if TYPE_CHECKING:
    from django.contrib.auth.models import User
else:
    User = get_user_model()

def make_authed_client(username: str = "testuser", password: str = "pass1234") -> Tuple[APIClient, User]:
    """
    Creates a Django user + DRF token and returns an APIClient with Authorization header set.
    """
    user = User.objects.create_user(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client, user
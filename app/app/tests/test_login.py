import pyotp
import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from allauth.mfa.models import Authenticator

# route setup
LOGIN = reverse("account_login")
MFA_AUTH = reverse("mfa_authenticate")
ADMIN_HOME = reverse("wagtailadmin_home")

# user setup
User = get_user_model()
PASSWORD = "correct-horse-battery-staple"
STAFF_USER = {"username": "admin", "email": "admin@example.com"}
NON_STAFF_USER = {"username": "member", "email": "member@example.com"}


# fixtures

def final_url(response):
    """
    The path where the user ends up, with any query string removed
    """
    if response.redirect_chain:
        return response.redirect_chain[-1][0].split("?")[0]
    return response.request["PATH_INFO"]


@pytest.fixture
def totp_secret():
    return pyotp.random_base32()


@pytest.fixture
def password():
    return PASSWORD


@pytest.fixture
def non_staff_user(db):
    return User.objects.create_user(
        username=NON_STAFF_USER["username"],
        email=NON_STAFF_USER["email"],
        password=PASSWORD,
        is_staff=False,
    )


@pytest.fixture
def staff_user(db):
    """
    Base staff user without TOTP
    """
    return User.objects.create_user(
        username=STAFF_USER["username"],
        email=STAFF_USER["email"],
        password=PASSWORD,
        is_staff=True,
    )


@pytest.fixture
def staff_user_with_totp(staff_user, totp_secret):
    Authenticator.objects.create(
        user=staff_user,
        type="totp",
        data={"secret": totp_secret},
    )
    return staff_user


@pytest.fixture
def current_totp(totp_secret):
    def _code():
        return pyotp.TOTP(totp_secret).now()
    return _code


# tests

@pytest.mark.django_db
@pytest.mark.usefixtures("staff_user_with_totp")
def test_password_and_valid_code_reaches_admin(client, password, current_totp):
    client.post(LOGIN, {"login": "admin", "password": password})
    response = client.post(MFA_AUTH, {"code": current_totp()})
    assert response.status_code == 302
    assert response["Location"] == ADMIN_HOME
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
@pytest.mark.usefixtures("staff_user_with_totp")
def test_password_alone_does_not_reach_admin(client, password):
    response = client.post(LOGIN, {"login": "admin", "password": password})
    assert response.status_code == 302
    assert response["Location"] == MFA_AUTH
    assert "_auth_user_id" not in client.session

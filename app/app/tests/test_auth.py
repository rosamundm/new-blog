import pytest
from django.contrib.auth import get_user_model
from sesame.utils import create_token

User = get_user_model()


@pytest.mark.django_db
class TestMagicLogin:
    @pytest.fixture
    def staff_user(self):
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_staff=True
        )

    def test_login_page_loads(self, client):
        response = client.get("/admin/login/")
        template_names = [t.name for t in response.templates]
        assert response.status_code == 200
        assert "wagtailadmin/login.html" in template_names

    def test_invalid_email_password(self, client):
        response = client.post(
            "/admin/login/",
            {"email": "test@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 200
        assert "Invalid email or password" in response.content.decode()

    def test_nonexistent_email(self, client):
        response = client.post(
            "/admin/login/",
            {"email": "nonexistent@example.com", "password": "testpass123"}
        )
        assert response.status_code == 200
        assert "Invalid email or password" in response.content.decode()

    def test_valid_email_password_sends_magic_link(
        self,
        client,
        staff_user,
        mailoutbox
    ):
        response = client.post(
            "/admin/login/",
            {"email": "test@example.com", "password": "testpass123"})
        template_names = [t.name for t in response.templates]

        # should show login_sent page
        assert response.status_code == 200
        assert "wagtailadmin/login_sent.html" in template_names

        # check email was sent
        assert len(mailoutbox) == 1
        assert "test@example.com" in mailoutbox[0].to
        assert "sesame=" in mailoutbox[0].body

    def test_sesame_login_with_valid_token(self, client, staff_user):
        token = create_token(staff_user)
        response = client.get(f"/admin/sesame-login/?sesame={token}")

        # should redirect to admin
        assert response.status_code == 302
        assert "/admin/" in response.url

    def test_sesame_login_with_invalid_token(self, client):
        response = client.get("/admin/sesame-login/?sesame=invalidtoken")

        # should redirect to login
        assert response.status_code == 302
        assert "/admin/login/" in response.url

    def test_sesame_login_already_authenticated(self, client, staff_user):
        token = create_token(staff_user)
        client.login(username="testuser", password="testpass123")
        response = client.get(f"/admin/sesame-login/?sesame={token}")

        # should redirect to admin
        assert response.status_code == 302
        assert "/admin/" in response.url

    def test_full_login_flow(self, client, staff_user, mailoutbox):
        # step 1: submit email + password
        response = client.post(
            "/admin/login/",
            {"email": "test@example.com", "password": "testpass123"}
        )
        assert response.status_code == 200
        assert len(mailoutbox) == 1

        # extract token from email
        email_body = mailoutbox[0].body
        token = email_body.split("sesame=")[1].split("\n")[0]

        # step 2: click the magic link
        response = client.get(f"/admin/sesame-login/?sesame={token}")

        # should redirect to admin
        assert response.status_code == 302
        assert "/admin/" in response.url

from django import forms
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.conf import settings
from sesame.utils import authenticate, create_token

User = get_user_model()


class UsernamePasswordForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


def magic_link_sent(request, email):
    return render(
        request,
        "wagtailadmin/login_sent.html",
        {"email": email}
    )


def invalid_credentials_error(request):
    return render(
        request,
        "wagtailadmin/login.html",
        {"error": "Invalid username or password"}
    )


def no_email_error(request):
    return render(
        request,
        "wagtailadmin/login.html",
        {"error": "User has no associated email address"}
    )


def magic_login(request):
    """
    2-step auth:
    - Regular email and password
    - Magic link sent to email
    """

    if request.method == "POST":
        form = UsernamePasswordForm(request.POST)

        if not form.is_valid():
            return invalid_credentials_error(request)

        # step 1
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)

        # step 2
        try:
            user = User.objects.get(username=username, is_staff=True)
            if user.check_password(password) and user.is_staff:
                token = create_token(user)
                token_link = f"/admin/sesame-login/?sesame={token}"
                magic_link = request.build_absolute_uri(token_link)

                # email isn't required when creating a user; check one exists!
                if not (email := user.email):
                    return no_email_error(request)

                send_mail(
                    "Your Wagtail admin login link",
                    f"Click here to log in: {magic_link}",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )

                return magic_link_sent(request, email)

            return invalid_credentials_error(request)

        except User.DoesNotExist:
            return invalid_credentials_error(request)

    return render(request, "wagtailadmin/login.html")


def sesame_login(request):
    """
    Authenticate with token and redirect to admin
    """

    if request.user.is_authenticated:
        return redirect("/admin/")

    if not (token := request.GET.get("sesame")):
        return redirect("wagtailadmin_login")

    user = authenticate(request, sesame=token)

    if user is not None:
        login(request, user, backend="sesame.backends.ModelBackend")
        return redirect("/admin/")

    return redirect("wagtailadmin_login")

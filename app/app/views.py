from django import forms
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.conf import settings
from sesame.utils import authenticate, create_token

User = get_user_model()


class EmailPasswordForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


def magic_link_sent(request, email):
    return render(request, "wagtailadmin/login_sent.html", {"email": email})


def invalid_credentials_error(request):
    return render(
        request,
        "wagtailadmin/login.html",
        {"error": "Invalid email or password"}
    )


def magic_login(request):
    """
    2-step auth:
    - Regular email and password
    - Magic link sent to email
    """

    if request.method == "POST":
        form = EmailPasswordForm(request.POST)

        if not form.is_valid():
            return invalid_credentials_error(request)

        # step 1
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=email, password=password)

        # step 2
        try:
            user = User.objects.get(email=email, is_staff=True)
            if user.check_password(password) and user.is_staff:
                token = create_token(user)
                token_link = f"/admin/sesame-login/?sesame={token}"
                magic_link = request.build_absolute_uri(token_link)

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

    user = authenticate(request)
    token = request.GET.get('sesame')

    if token:
        user = authenticate(request, sesame=token)

    if user is not None:
        login(request, user, backend="sesame.backends.ModelBackend")
        return redirect("/admin/")

    # if auth fails, send them back to login
    return redirect("wagtailadmin_login")

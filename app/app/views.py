from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.conf import settings
from sesame.utils import authenticate, create_token

User = get_user_model()


def sesame_login(request):
    """
    Authenticate using sesame token and redirect to admin
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


def magic_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email, is_staff=True)
            token = create_token(user)
            token_link = f"/admin/sesame-login/?sesame={token}"
            magic_link = request.build_absolute_uri(token_link)
            send_mail(
                "Your Wagtail admin login link",
                f"Click here to log in: {magic_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            return render(
                request,
                "wagtailadmin/login_sent.html",
                {"email": email}
            )
        except User.DoesNotExist:
            return render(
                request,
                "wagtailadmin/login.html",
                {"error": "No staff account found with that email"}
            )

    return render(request, "wagtailadmin/login.html")

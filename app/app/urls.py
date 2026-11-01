from django.conf import settings
from django.urls import include, path
from django.views.generic import RedirectView

from search import views as search_views

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from wagtail_footnotes import urls as footnotes_urls

ADMIN_SUFFIX = settings.ADMIN_SUFFIX
AUTH_SUFFIX = settings.AUTH_SUFFIX

urlpatterns = [
    # redirect Wagtail login page to AllAuth (must come first):
    path(
        f"{ADMIN_SUFFIX}login/",
        RedirectView.as_view(pattern_name="account_login", query_string=True),
    ),
    # AllAuth login, logout, account pages:
    path(f"{AUTH_SUFFIX}", include("allauth.urls")),
    # AllAuth 2FA pages:
    path(f"{AUTH_SUFFIX}", include("allauth.mfa.urls")),
    # Wagtail admin:
    path(f"{ADMIN_SUFFIX}", include(wagtailadmin_urls)),

    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),

    # Wagtail footnotes:
    path("footnotes/", include(footnotes_urls)),

    # Sentry tripwire:
    # path("sentry-debug/", trigger_error = lambda request: 1 / 0),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]

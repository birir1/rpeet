"""
Root URL configuration for the KCK API.

All application endpoints are prefixed with /kck/ to namespace them clearly when the
API sits behind a reverse proxy alongside other services. The health check endpoint is
intentionally at the root level (/health/) rather than under /kck/ so that load balancers
and monitoring tools can probe it without needing to know about our application namespace.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path

from apps.analytics.urls import settings_urlpatterns
from apps.common.views import ImageUploadView


def health_check(request):
    """
    GET /health/ -- lightweight health probe for load balancers and uptime monitors.

    We execute a minimal "SELECT 1" query to verify database connectivity. This catches
    both DB server outages and connection pool exhaustion. Returns 503 if the DB is
    unreachable so load balancers can route traffic to healthy instances.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False

    status_code = 200 if db_ok else 503
    return JsonResponse({
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
    }, status=status_code)


urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("admin/", admin.site.urls),
    path("kck/auth/", include("apps.users.urls_auth")),
    path("kck/users/", include("apps.users.urls")),
    path("kck/memberships/", include("apps.users.urls_memberships")),
    path("kck/leaders/", include("apps.leaders.urls")),
    path("kck/comms/", include("apps.communications.urls")),
    path("kck/announcements/", include("apps.communications.urls_announcements")),
    path("kck/certs/", include("apps.certificates.urls")),
    path("kck/events/", include("apps.events.urls")),
    path("kck/analytics/", include("apps.analytics.urls")),
    path("kck/settings/", include(settings_urlpatterns)),
    path("kck/media/upload/", ImageUploadView.as_view(), name="media-upload"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

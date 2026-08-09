from django.contrib import admin
from django.urls import path, include
from patient import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("patient.urls")),
    path(
        "profile/",
         views.insurance_profile,
         name="insurance_profile",
),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
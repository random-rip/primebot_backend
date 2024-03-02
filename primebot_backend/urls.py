from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('.admin/', admin.site.urls, name="admin"),
    path('api/', include('app_api.urls')),
    path(r"i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

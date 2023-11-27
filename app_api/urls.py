from django.shortcuts import redirect
from django.urls import include, path, re_path
from rest_framework.decorators import api_view


@api_view(['GET'])
def version_v1_redirect(request, *args, **kwargs):
    url = "/api/v1/" + request.path.lstrip("/api/")
    query_string = request.META.get('QUERY_STRING', '')
    if query_string:
        url += f"?{query_string}"
    return redirect(to=url, *args, permanent=True, **kwargs)


urlpatterns = [
    path("v1/", include(("app_api.api_v1.urls", "app_api.api_v1"), namespace='v1')),
    re_path(r'^(?!v\d).*$', version_v1_redirect),
]

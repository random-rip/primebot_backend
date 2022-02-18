from django.urls import path

from app_api.modules.status import views

urlpatterns = [
    path('', views.StatusView.as_view(), ),
]

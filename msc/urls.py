from django.contrib import admin
from django.urls import include, path

from django.contrib.auth import views as auth_views
from .questionnaire.views import questionnaire_list, questionnaire_detail

urlpatterns = [
    path("forms", include("msc.forms.urls"),),
    path("admin/", admin.site.urls),
    path("accounts/", include('django.contrib.auth.urls')),
    path("", questionnaire_list, name="questionnaire-list"),
    path("take-questioner/<int:pk>/", questionnaire_detail, name="questionnaire-detail"),
]


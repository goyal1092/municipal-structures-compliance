from django.contrib import admin
from django.urls import include, path

from django.contrib.auth import views as auth_views
from .questionnaire.views import questionnaire_list, questionnaire_list_submitted, QuestionnaireDetail
from .organisation.views import login
from .response.views import save_response

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include('django.contrib.auth.urls')),
    path("login/", login, name="custom-login"),
    path("", questionnaire_list, name="root"),
    path("forms/active/", questionnaire_list, name="forms-active"),
    path("forms/submitted/", questionnaire_list_submitted, name="forms-submitted"),
    path("forms/<int:pk>/", QuestionnaireDetail.as_view(), name="questionnaire-detail"),
    # path("save-response/", save_response, name="save-response"),
]


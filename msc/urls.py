from django.contrib import admin
from django.urls import include, path

from django.contrib.auth import views as auth_views
from .questionnaire.views import questionnaire_list, QuestionnaireDetail
from .organisation.views import login
from .response.views import save_response

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include('django.contrib.auth.urls')),
    path("login/", login, name="custom-login"),
    path("", questionnaire_list, name="questionnaire-list"),
    path("take-questioner/<int:pk>/", QuestionnaireDetail.as_view(), name="questionnaire-detail"),
    # path("save-response/", save_response, name="save-response"),
]


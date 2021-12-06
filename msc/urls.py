from django.contrib import admin
from django.urls import include, path

from django.contrib.auth import views as auth_views
from .questionnaire.views import (
    questionnaire_list, questionnaire_list_submitted,
    QuestionnaireDetail, active_form_summary_view, submited_form_view,
    QuestionnaireDetailPreview
)
from .organisation.views import login, send_reminder
from .response.views import save_response
from .reporting.views import download_report

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include('django.contrib.auth.urls')),
    path("login/", login, name="custom-login"),
    path("", questionnaire_list, name="root"),
    path("forms/active/", questionnaire_list, name="forms-active"),
    path("forms/submitted/", questionnaire_list_submitted, name="forms-submitted"),
    path("forms/<int:pk>/", QuestionnaireDetail.as_view(), name="questionnaire-detail"),
    path('ckeditor', include('ckeditor_uploader.urls')),
    path("save-response/", save_response, name="save-response"),
    path("send_reminder/", send_reminder, name="send_reminder"),
    path("forms/<int:pk>/summary", active_form_summary_view, name="form-summary"),
    path("forms/submitted/<int:questionnaire_id>/<int:organisation_id>/", submited_form_view, name="form-submitted-response"),
    path("download/report/<int:questionnaire_id>/", download_report, name="download-report"),
    path("forms/<int:pk>/preview/", QuestionnaireDetailPreview.as_view(), name="form-preview"),
]

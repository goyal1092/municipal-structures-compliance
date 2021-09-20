import string

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Questionnaire
from .utils import get_serialized_questioner, check_user_org
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from msc.organisation.models import Organisation
from msc.response.views import save_response, submit_form
from msc.response.models import Response

from django.views.generic import TemplateView


@check_user_org
@login_required
def questionnaire_list(request):
    context = {
        "questionnaires": Questionnaire.objects.filter(is_published=True),
    }
    return render(request, 'questionnaire/list.html', context)



class QuestionnaireDetail(TemplateView):
    template_name = 'questionnaire/questionnaire_form.html'

    @method_decorator(login_required)
    @method_decorator(check_user_org)
    def dispatch(self, *args, **kwargs):
        return super(ThankYouView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        questionnaire = get_object_or_404(Questionnaire, pk=pk)
        organisation = request.user.organisation
        context = {
            "questionnaire": questionnaire,
            "sections": get_serialized_questioner(questionnaire, organisation)
        }
        return render(request, 'questionnaire/questionnaire_form.html', context)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        questionnaire = get_object_or_404(Questionnaire, pk=pk)
        organisation = request.user.organisation

        response, created = Response.objects.get_or_create(
            questionnaire=questionnaire, organisation=organisation
        )
        form_save_type = "save"
        if response.is_submitted:
            response.is_submitted = False
            response.save()

        is_submitted = request.POST.get("submit_form", None) == "submit"
        context = {}

        validation_errors = save_response(request, organisation, questionnaire, response)
        if is_submitted:
            form_save_type = "submission"
            submission_errors = submit_form(questionnaire, response)
            if not submission_errors and not validation_errors:
                response.is_submitted = True
                response.save()

            context["submission_errors"] = submission_errors

        context.update({
            "questionnaire": questionnaire,
            "errors": validation_errors,
            "sections": get_serialized_questioner(questionnaire, organisation),
            "form_save_type": form_save_type
        })
        return render(request, 'questionnaire/questionnaire_form.html', context)
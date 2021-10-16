import string

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.generic import TemplateView

from msc.organisation.models import Organisation
from msc.response.views import save_response, submit_form
from msc.response.models import Response
from msc.authentication.models import Share

from .models import Questionnaire
from .utils import get_serialized_questioner, check_user_org


@login_required
@check_user_org
def questionnaire_list(request):
    user = request.user
    organisation = user.organisation

    questionnaire_ids = Share.objects.filter(
        target_content_type__model="questionnaire",
        sharer_content_type__model="organisation",
        sharer_object_id=organisation.id
    ).values_list("target_object_id", flat=True)

    filters = {
        "is_published": True, "id__in":questionnaire_ids,
        "start__lte": timezone.now()
    }

    if not user.is_admin or not user.is_national or not user.is_provincial:
        filters["close__gte"] = timezone.now()


    context = {
        "questionnaires": Questionnaire.objects.filter(**filters),
    }

    template_name = 'questionnaire/list.html'
    if user.is_national or user.is_provincial:
        template_name = 'questionnaire/admin_list.html'
    return render(request, template_name, context)

def questionnaire_list_submitted(request):

    user = request.user
    organisation_ids = [user.organisation.id]
    if user.is_national:
        organisation_ids = Organisation.objects.values_list(
            "id", flat=True
        )
    elif user.is_provincial:
        organisation_ids = user.organisation.get_children().values_list(
            "id", flat=True
        )

    questionnaire_ids = Share.objects.filter(
        target_content_type__model="questionnaire",
        sharer_content_type__model="organisation",
        sharer_object_id=user.organisation.id,
    ).values_list("target_object_id", flat=True)

    responses = Response.objects.filter(
        questionnaire_id__in=questionnaire_ids,
        questionnaire__is_published=True,
        is_submitted=True,
        organisation_id__in=organisation_ids
    )
    context = {
        "responses": responses
    }
    return render(request, 'questionnaire/list-submitted.html', context)

class QuestionnaireDetail(TemplateView):
    template_name = 'questionnaire/questionnaire_form.html'

    @method_decorator(login_required)
    @method_decorator(check_user_org)
    def dispatch(self, request, *args, **kwargs):
        questionnaire = get_object_or_404(Questionnaire, pk=kwargs["pk"])
        share = Share.objects.filter(
            target_content_type__model="questionnaire",
            sharer_content_type__model="organisation",
            sharer_object_id=request.user.organisation.id,
            target_object_id=questionnaire.id
        ).first()
        if (
            not share or questionnaire.start > timezone.now() or not questionnaire.is_published
        ):
            return redirect("forms-active")

        return super().dispatch(request, *args, **kwargs)

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

        validation_errors = save_response(
            request, organisation, questionnaire, response)
        if is_submitted:
            form_save_type = "submission"
            submission_errors = submit_form(questionnaire, response)
            if not submission_errors and not validation_errors:
                response.is_submitted = True
                response.save()
                messages.success(request, f"Submitted {questionnaire.name} form successfully" )
                return redirect("forms-submitted")

            context["submission_errors"] = submission_errors

        context.update({
            "questionnaire": questionnaire,
            "errors": validation_errors,
            "sections": get_serialized_questioner(questionnaire, organisation),
            "form_save_type": form_save_type
        })
        return render(request, 'questionnaire/questionnaire_form.html', context)

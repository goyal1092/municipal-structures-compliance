import string

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import Http404
from django.urls import reverse

from msc.questionnaire.models import Questionnaire
from msc.organisation.models import Organisation, Group
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


    questionnaires = Questionnaire.objects.filter(**filters)
    questionnaire_list = []

    for questionnaire in questionnaires:
        if not questionnaire.is_submitted(request.user.organisation):
            total_questions = questionnaire.question_count
            response_count = questionnaire.question_response_count(request.user.organisation)
            perc = 0.0

            if total_questions > 0:
                perc = round((float(response_count)/total_questions)*100,1)
            questionnaire_list.append({
                "obj": questionnaire,
                "response_count": response_count,
                "total_questions": total_questions,
                "per_completed": perc
            })

    context = {
        "questionnaires": questionnaire_list
    }

    template_name = 'questionnaire/list.html'
    if user.is_national or user.is_provincial:
        template_name = 'questionnaire/admin_list.html'
    return render(request, template_name, context)

@login_required
@check_user_org
def questionnaire_list_submitted(request):

    user = request.user
    organisation_ids = [user.organisation.id]

    filters = {
        "forms": [],
        "org_type": {},
        "selected": {}
    }

    if user.is_national:
        organisation_ids = Organisation.objects.values_list(
            "id", flat=True
        )
        for org_type in Group.objects.all().exclude(id=user.organisation.org_type_id):
            filters["org_type"][org_type.name] = Organisation.objects.filter(org_type=org_type)

    elif user.is_provincial:
        organisations = user.organisation.get_children(include_self=False)
        organisation_ids = organisations.values_list(
            "id", flat=True
        )

        org_types = organisations.values_list("org_type__name", flat=True).distinct()

        for org_type in org_types:
            filters["org_type"][org_type] = Organisation.objects.filter(
                org_type__name=org_type, parent=user.organisation
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
    forms = Questionnaire.objects.filter(
        id__in=responses.values_list("questionnaire_id", flat=True)
    ).distinct()

    filters["forms"] = forms
    search = request.GET.get("search", '')

    if search.strip():
        responses = responses.filter(
            Q(questionnaire__name__icontains=search.strip()) |
             Q(organisation__name__icontains=search.strip())
        )
        filters["selected"]["search"] = search.strip()



    form = request.GET.get("form", None)
    if form:
        responses = responses.filter(questionnaire_id=form)
        filters["selected"]["form"] = int(form)

    org_filter = [int(x) for x in request.GET.getlist("organisation", []) if x.isnumeric()]
    if org_filter:
        organisations_to_filter = []
        for o in Organisation.objects.filter(id__in=org_filter):
            organisations_to_filter = organisations_to_filter + list(o.get_children())
        responses = responses.filter(organisation__in=organisations_to_filter)
        filters["selected"]["organisation"] = org_filter

    p = Paginator(responses, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)

    context = {
        "page_obj": page_obj,
        "filters": filters,
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

        if request.user.is_national or request.user.is_provincial:
            return redirect(reverse('form-preview', kwargs={"pk": kwargs["pk"]}))

        response = Response.objects.filter(
            questionnaire=questionnaire, organisation=request.user.organisation,
            is_submitted=True
        ).first()

        if response:
            return redirect(reverse('form-submitted-response', kwargs={
                "questionnaire_id": kwargs["pk"],
                "organisation_id": request.user.organisation.id
            }))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        questionnaire = get_object_or_404(Questionnaire, pk=pk)
        organisation = request.user.organisation

        total_questions = questionnaire.question_count
        response_count = questionnaire.question_response_count(request.user.organisation)
        perc = 0.0

        if total_questions > 0:
            perc = round((float(response_count)/total_questions)*100,1)
        context = {
            "questionnaire": questionnaire,
            "sections": get_serialized_questioner(questionnaire, organisation),
            "response_count": response_count,
            "total_questions": total_questions,
            "per_completed": perc
        }
        return render(request, 'questionnaire/questionnaire_form.html', context)


    def post(self, request, *args, **kwargs):

        pk = kwargs.get("pk", None)
        questionnaire = get_object_or_404(Questionnaire, pk=pk)
        organisation = request.user.organisation
        context = {}
        validation_errors = {}

        response, created = Response.objects.get_or_create(
            questionnaire=questionnaire, organisation=organisation
        )

        form_save_type = "save"
        if not response.is_submitted:
            is_submitted = request.POST.get("submit_form", None) == "submit"
            validation_errors = save_response(request, questionnaire, response)

            if is_submitted:
                form_save_type = "submission"
                submission_errors = submit_form(questionnaire, response)
                if not submission_errors and not validation_errors:
                    response.is_submitted = True
                    response.save()
                    messages.success(request, f"Submitted {questionnaire.name} form successfully" )
                    return redirect("forms-submitted")

                context["submission_errors"] = submission_errors

        total_questions = questionnaire.question_count
        response_count = questionnaire.question_response_count(request.user.organisation)
        perc = 0.0

        if total_questions > 0:
            perc = round((float(response_count)/total_questions)*100,1)

        context.update({
            "questionnaire": questionnaire,
            "errors": validation_errors,
            "sections": get_serialized_questioner(questionnaire, organisation),
            "form_save_type": form_save_type,
            "response_count": response_count,
            "total_questions": total_questions,
            "per_completed": perc
        })
        return render(request, 'questionnaire/questionnaire_form.html', context)


@login_required
@check_user_org
def active_form_summary_view(request, pk):
    user = request.user
    organisation = user.organisation
    questionnaire = get_object_or_404(Questionnaire, pk=pk)

    if not user.is_national and not user.is_provincial:
        raise Http404

    context = {
        "questionnaire": questionnaire,
        "sections": get_serialized_questioner(questionnaire, None),
    }
    return render(request, "questionnaire/active_form_summary_view.html", context)


@login_required
@check_user_org
def submited_form_view(request, questionnaire_id, organisation_id):
    user = request.user
    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    organisation = get_object_or_404(Organisation, pk=organisation_id)

    if not user.is_national:
        organisations = user.organisation.get_children()
        if organisation not in organisations:
            raise Http404

    response = Response.objects.filter(
        organisation=organisation, questionnaire=questionnaire
    ).first()
    total_questions = questionnaire.question_count
    qr_responses = response.questionresponse_set.filter(
        question__parent__isnull=True
    ).count()
    context = {
        "questionnaire": questionnaire,
        "sections": get_serialized_questioner(questionnaire, organisation),
        "organisation": organisation,
        "response": response,
        "total_questions_count": total_questions,
        "qr_responses_count": qr_responses,
        "perc_completed":  (float(qr_responses)/total_questions)*100,
    }
    return render(request, 'questionnaire/submitted_form_view.html', context)


class QuestionnaireDetailPreview(TemplateView):
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

        if not request.user.is_national and not request.user.is_provincial:
            return redirect(reverse('questionnaire-detail', kwargs={"pk": kwargs["pk"]}))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        questionnaire = get_object_or_404(Questionnaire, pk=pk)
        organisation = request.user.organisation

        total_questions = questionnaire.question_count
        response_count = 0
        perc = 0.0

        if total_questions > 0:
            perc = round((float(response_count)/total_questions)*100,1)
        context = {
            "questionnaire": questionnaire,
            "sections": get_serialized_questioner(questionnaire, organisation),
            "response_count": response_count,
            "total_questions": total_questions,
            "per_completed": perc
        }
        return render(request, 'questionnaire/questionnaire_preview_form.html', context)

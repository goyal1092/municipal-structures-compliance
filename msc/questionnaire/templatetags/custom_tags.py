from django import template
from msc.questionnaire.models import Questionnaire
from msc.organisation.models import Organisation
from msc.authentication.models import Share

from django.template.loader import get_template

register = template.Library()


from django.conf import settings
from msc.questionnaire.models import Questionnaire



@register.filter
def keyvalue(dict, key):
    try:
        return dict[key]
    except KeyError:
        return ''

@register.filter
def split_timeuntil(duration):
    return duration.split(",")[0]

@register.filter
def reminder_options(questionnaire, user):
    return questionnaire.get_reminder_options(user)


@register.filter
def submitted_questionnaires(questionnaire, user):
    submitted_response_count = questionnaire.response_set.filter(
        is_submitted=True
    ).count()
    total_count = 0

    organisation_ids = Share.objects.filter(
        relationship="viewer",
        target_content_type__model="questionnaire",
        sharer_content_type__model="organisation",
        target_object_id=questionnaire.id
    ).values_list("sharer_object_id", flat=True)

    if user.is_national:
        total_count = len(organisation_ids)

    elif user.is_provincial:
        total_count = Organisation.objects.filter(
            id__in=organisation_ids, parent=user.organisation
        ).count()
    
    #TODO: Better way to prevent division by zero
    if total_count == 0:
        total_count = 1

    html = get_template(f"subtemplate/progress_bar.html").render({
        "text": f'{submitted_response_count}/{total_count}',
        "per": round((float(submitted_response_count)/total_count)*100,1),
    })

    return html


@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()

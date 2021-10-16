from django import template
from msc.questionnaire.models import Questionnaire
from msc.organisation.models import Organisation
from msc.authentication.models import Share

from django.template.loader import get_template

register = template.Library()

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

    html = get_template(f"subtemplate/progress_bar.html").render({
        "text": f'{submitted_response_count}/{total_count}',
        "per": (submitted_response_count/total_count)*100,
    })

    return html
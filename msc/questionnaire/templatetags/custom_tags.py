from django import template
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

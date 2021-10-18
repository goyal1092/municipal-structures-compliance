from django.db import models
from msc.questionnaire.base import MSCBase

from django.conf import settings

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives


class Group(MSCBase):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Organisation(MSCBase):
    name = models.CharField(max_length=256)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True)
    org_type = models.ForeignKey(
        "Group", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_children(self, include_self=True):
        org_ids = []
        if include_self:
            org_ids.append(self.id)

        org_ids = org_ids + list(
            Organisation.objects.filter(
                parent=self).values_list("id", flat=True)
        )
        return Organisation.objects.filter(id__in=org_ids)


class EmailActivity(MSCBase):
    questionnaire = models.ForeignKey(
        "questionnaire.Questionnaire", on_delete=models.CASCADE, null=True, blank=True
    )
    activity_type = models.CharField(
        max_length=32, choices=settings.EMAIL_ACTIVITY_TYPE)
    to_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="users")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="sender")
    org_user_filter = models.CharField(max_length=100, null=True, blank=True)
    user_msg = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.activity_type} -> {self.questionnaire}"

    def get_reminder_subject(self):
        return f"Reminder to fill out {self.questionnaire.name} form"

    def get_reminder_context(self):
        return {
            "questionnaire": self.questionnaire,
            "user_msg": self.user_msg,
            "link": reverse('questionnaire-detail', args=(self.questionnaire.id,))
        }

    def get_account_activation_context(self):
        return {
            "link": reverse("password_change")
        }

    def get_subject(self):
        try:
            subject = getattr(self, "get_%s_subject" % self.activity_type)()
        except AttributeError:
            subject = 'DCOG Tool Notification'
        return subject

    def get_context(self, context):
        try:
            to_update = getattr(self, "get_%s_context" % self.activity_type)()
            context.update(to_update)
        except AttributeError as e:
            pass
        return context

    def send_email(self, request, **kwargs):
        context = self.get_context(kwargs)
        subject = self.get_subject()
        print(settings.DEFAULT_FROM_EMAIL)
        from_address = settings.DEFAULT_FROM_EMAIL
        protocol = "https://" if request.is_secure() else "http://"
        context.update({
            "sender": self.user,
            "base_url": f"{protocol}{request.get_host()}"
        })
        to = [u.email for u in self.to_users.all()]

        text = get_template(
            f"emailTemplates/{self.activity_type}.txt").render(context)
        html = get_template(
            f"emailTemplates/{self.activity_type}.html").render(context)

        if not text and not html:
            raise Exception("Email body cannot be empty")

        msg = EmailMultiAlternatives(subject, text, from_address, to)
        if html:
            msg.attach_alternative(html, "text/html")

        if to and msg:
            return msg.send()

    @property
    def is_national(self):
        return self.parent == None

    @property
    def is_provincial(self):
        return self.parent and self.parent.parent == None

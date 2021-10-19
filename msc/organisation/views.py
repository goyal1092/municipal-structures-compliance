import json

from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from msc.questionnaire.models import Questionnaire
from .models import EmailActivity


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        organisation_id = request.POST.get('organisation_id', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            if not user.organisation:
                messages.error(request, 'User Does not belong to any organisation')
            if user.is_active and user.organisation:
                auth_login(request, user)
                return redirect('forms-active')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'registration/login.html')


def send_reminder(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            questionnaire_id = int(data.get('questionnaire_id', None))
            questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
        except Exception as e:
            return JsonResponse({'status':'false'}, status=405)

        user_msg = data.get("msg", None)
        selected_option = data.get("selected_option", None)
        reminder_options = questionnaire.get_reminder_options(request.user)
        option = next((item for item in reminder_options if item["name"] == selected_option), None)
        if option:
            organisations = option["organisations"]
            for organisation in organisations:
                activity = EmailActivity.objects.create(
                    questionnaire=questionnaire, activity_type="reminder",
                    org_user_filter=selected_option, user=request.user, user_msg=user_msg
                )
                activity.to_users.add(*list(organisation.user_set.all()))
                activity.send_email(request)

            return JsonResponse({'status':'true'}, status=200)

    return JsonResponse({'status':'false'}, status=405)
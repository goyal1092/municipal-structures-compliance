from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        organisation_id = request.POST.get('organisation_id', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            user_organisations = user.organisation_set.all().values_list("id", flat=True)
            selected_org = None
            if len(user_organisations) == 0:
                messages.error(request, 'User Does not belong to any organisation')
            elif organisation_id:
                if organisation_id in user_organisations:
                    selected_org = organisation_id
                else:
                    messages.error(request, 'User does not belong to organisation')
            else:
                selected_org = user_organisations[0]

            if user.is_active and selected_org:
                auth_login(request, user)
                request.session["organisation_id"] = selected_org
                return redirect('questionnaire-list')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'registration/login.html', context)
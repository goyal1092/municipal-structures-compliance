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
            if not user.organisation:
                messages.error(request, 'User Does not belong to any organisation')
            if user.is_active and user.organisation:
                auth_login(request, user)
                return redirect('questionnaire-list')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'registration/login.html', context)
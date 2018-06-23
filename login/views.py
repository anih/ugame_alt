# -*- coding: utf-8 -*-
# from login.models import User
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

from utils.jinja.fun_jinja import jrender


def main(request):
    if "username" in request.POST and "password" in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect('/game/main/')
        elif user is not None and not user.is_active:
            return jrender(request, 'main/index.html', {"msg": "Konto nieaktywne, odbierz emaila z linkiem i aktywuj"})
        else:
            return jrender(request, 'main/index.html', {"msg": "Błędne hasło lub login"})
    else:
        return jrender(request, 'main/index.html', {})


def log_hidden(request):
    if "username" in request.POST and "password" in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect('/game/main/')
        else:
            return jrender(request, 'main/index.html', {})
    else:
        return jrender(request, 'main/index.html', {})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

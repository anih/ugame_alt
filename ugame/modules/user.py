# -*- coding: utf-8 -*-
from datetime import datetime

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.contrib import messages

from ..generic.cms_metaclass import CmsMetaclass
from ..generic.constants import MODULE_AUTH_SESSION_KEY
from ugame.forms.forms import UserCreationForm
from utils.jinja.filters import url


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def admin_mine_login(self, user):
        """
        Persist a user id and a backend in the request. This way a user doesn't
        have to reauthenticate on every request.
        """
        if user is None:
            user = self.user
            # TODO: It would be nice to support different login methods, like signed cookies.
        user.last_login = datetime.now()
        user.save()

        if MODULE_AUTH_SESSION_KEY in self.request.session:
            if self.request.session[MODULE_AUTH_SESSION_KEY] != user.id:
                self.request.session.clear()
        self.request.session[MODULE_AUTH_SESSION_KEY] = user.id
        if hasattr(self.request, self.application):
            setattr(self.request, self.application, user)

    def admin_mine_logout(self):
        if MODULE_AUTH_SESSION_KEY in self.request.session:
            del self.request.session[MODULE_AUTH_SESSION_KEY]
        if hasattr(self.request, self.application):
            setattr(self.request, self.application, AnonymousUser())

    def site_login(self):
        if 'username' in self.request.POST and 'password' in self.request.POST:
            username = self.request.POST['username']
            password = self.request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                self.admin_mine_login(user)
                if 'next' in self.request.REQUEST and self.request.REQUEST["next"] != reverse(self.urls.logout):
                    return HttpResponseRedirect(self.request.REQUEST['next'])
                return HttpResponseRedirect(reverse(self.all_urls.main.main))
            else:
                messages.error(self.request, message="Zły login lub hasło")
                return {}
        else:
            return {}

    site_login.without_user = True

    def site_logout(self):
        self.admin_mine_logout()
        return HttpResponseRedirect(reverse(self.all_urls.main.main))

    def site_registration(self):
        form = UserCreationForm()

        if self.request.method == 'POST':
            form = UserCreationForm(data=self.request.POST)
            if form.is_valid():
                user = form.save()
                self._mine_login(user)
                messages.info(self.request, message="Dziękujemy za zarejestrowanie się")

                #RegistrationEmailTask.delay_countdown(user.id)

                if 'next' in self.request.REQUEST and self.request.REQUEST["next"] != url(self.urls.registration):
                    return HttpResponseRedirect(self.request.REQUEST['next'])
                return HttpResponseRedirect(url(self.all_urls.main.main))

        return {
            "form": form,
        }

    site_registration.without_user = True
    site_registration.url = "zarejestruj/{r}$"
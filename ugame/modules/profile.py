# -*- coding: utf-8 -*-
import datetime
import random
from hashlib import sha1

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseRedirect

from settings import DEFAULT_FROM_EMAIL, URL
from ugame.forms.forms import ChangePassMail, UserprofileForm
from ugame.models import send_info_message
from ugame.models.all import StareMaile, UserProfile, ZmianaHasla, ZmianaMaila
from ugame.topnav import topnav_site
from utils.jinja.filters import url
from utils.jinja.fun_jinja import render_to_string
from ..generic.cms_metaclass import CmsMetaclass


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_change_pass(self, activation_key):
        data_mozliwa = datetime.datetime.now() - datetime.timedelta(days=1)
        zmiany = ZmianaHasla.objects.select_for_update().filter(hash=activation_key, data__gte=data_mozliwa)
        for z in zmiany:
            user = User.objects.select_for_update().get(pk=z.user_id)
            user.set_password(z.haslo)
            user.save(force_update=True)
            message = "Zmiana hasła powiodła się"
            send_info_message(user=user, message=message)
            z.delete()
        return HttpResponseRedirect(url(self.urls.edit))

    def site_change_email(self, activation_key):
        data_mozliwa = datetime.datetime.now() - datetime.timedelta(days=1)
        zmiany = ZmianaMaila.objects.select_for_update().filter(hash=activation_key, data__gte=data_mozliwa)
        for z in zmiany:
            user = User.objects.select_for_update().get(pk=z.user_id)
            StareMaile.objects.create(user=user, email=user.email)
            user.email = z.email
            user.save(force_update=True)
            message="Zmiana emaila powiodła się"
            send_info_message(user=user, message=message)
            z.delete()
        return HttpResponseRedirect(url(self.urls.edit))

    def site_edit(self):
        current_planet = self.game.get_current_planet()

        if self.game.userprofile:
            if self.request.method == 'POST':

                form_change = ChangePassMail(self.request.POST)
                print form_change.errors
                if form_change.is_valid():
                    pass1 = form_change.cleaned_data['password1']
                    pass2 = form_change.cleaned_data['password2']
                    email = form_change.cleaned_data['email']
                    if pass1 == pass2 and len(pass1) >= 5:
                        salt = sha1(str(random.random())).hexdigest()[:5]
                        activation_key = sha1(salt + pass1).hexdigest()
                        ZmianaHasla.objects.create(user=self.game.user, haslo=pass1, hash=activation_key)
                        message = render_to_string('mail/change.txt',
                                                   {'link': '%s/change_pass/%s' % (URL, activation_key)})
                        subject = 'Link z %s' % (URL,)
                        subject = ''.join(subject.splitlines())
                        send_mail(subject, message, DEFAULT_FROM_EMAIL, [self.game.user.email])
                        message="Żeby dokończyć zmianę hasła, odbierz pocztę z emaila i kliknij w link"
                        send_info_message(user=self.game.user, message=message)

                    if email:
                        salt = sha1(str(random.random())).hexdigest()[:5]
                        activation_key = sha1(salt + email).hexdigest()
                        ZmianaMaila.objects.create(user=self.game.user, email=email, hash=activation_key)
                        message = render_to_string('mail/change.txt',
                                                   {'link': '%s/change_email/%s' % (URL, activation_key)})
                        subject = 'Link z %s' % (URL,)
                        subject = ''.join(subject.splitlines())
                        send_mail(subject, message, DEFAULT_FROM_EMAIL, [self.game.user.email])
                        message="Żeby dokończyć zmianę emaila, odbierz pocztę ze starego emaila i kliknij w link"
                        send_info_message(user=self.game.user, message=message)
                form = UserprofileForm(self.request.POST, self.request.FILES, instance=self.game.userprofile)
                if form.is_valid():
                    obj = form.save(commit=False)
                    if not obj.avatar:
                        obj.avatar = self.game.userprofile.avatar
                    obj.save()  # tu tak ma byc
                    print "udalo sie2 :)"
                    return HttpResponseRedirect(url(self.url))
            else:
                form = UserprofileForm(instance=self.game.userprofile)
                form_change = ChangePassMail()

            topnav = topnav_site(self.game)
            return {"topnav": topnav, "form": form, 'form_change': form_change,
                    "u": self.game.userprofile}
        return HttpResponseRedirect(url(self.all_urls.main.main))

    def site_show(self, object_id):
        try:
            userprofile = UserProfile.objects.get(pk=object_id)
        except UserProfile.DoesNotExist:
            return HttpResponseRedirect(url(self.all_urls.main.main))
        topnav = topnav_site(self.game)
        return {"u": userprofile, "topnav": topnav}

# -*- coding: utf-8 -*-
import random
import string
from time import strftime

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect

from ..generic.cms_metaclass import CmsMetaclass
from ugame.forms.forms import RaportujTemat
from ugame.topnav import topnav_site
from ugame.models.all import UserProfile, Tematy, TematyMod, WiadomosciMod, Wiadomosci
from utils.jinja.filters import url


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_report(self, object_id):
        try:
            temat = Tematy.objects.get(pk=object_id)
        except Tematy.DoesNotExist:
            return HttpResponseRedirect(url(self.main.main))

        if self.request.method == 'POST':
            form = RaportujTemat(data=self.request.POST)
            if form.is_valid():
                t_rap = TematyMod.objects.create(powod=form.cleaned_data['powod'],
                                                 kto_raportowal=self.game.user, nadawca=temat.nadawca,
                                                 odbiorca=temat.odbiorca, temat=temat.temat, data=temat.data)
                for w in temat.wiadomosci_set.all():
                    WiadomosciMod.objects.create(temat=t_rap, tekst=w.tekst, kto=w.kto, data=w.data)
                self.game.send_message("Raport został przyjęty")
                return HttpResponseRedirect(url(self.url.list))
        else:
            form = RaportujTemat()
        topnav = topnav_site(self.game)
        return {"topnav": topnav, "temat": temat, "form": form}

    def site_list(self):
        tematy = Tematy.objects.filter(
            (Q(nadawca=self.game.user) & Q(n_del='N')) | (Q(odbiorca=self.game.user) & Q(o_del='N'))).order_by("-data")
        self.game.userprofile.new_message = 0

        topnav = topnav_site(self.game)
        return {"topnav": topnav, "tematy": tematy}

    def site_delete(self, object_id):
        try:
            temat = Tematy.objects.get(Q(pk=object_id), Q(nadawca=self.game.user) | Q(odbiorca=self.game.user))
            if self.game.user == temat.odbiorca:
                if temat.n_del == 'T':
                    Wiadomosci.objects.filter(temat=temat).delete()
                    temat.delete()
                else:
                    temat.o_del = 'T'
                    temat.save(force_update=True)
            elif self.game.user == temat.nadawca:
                if temat.o_del == 'T':
                    Wiadomosci.objects.filter(temat=temat).delete()
                    temat.delete()
                else:
                    temat.n_del = 'T'
                    temat.save(force_update=True)
        except Tematy.DoesNotExist:
            pass
        return HttpResponseRedirect(url(self.urls.list))

    def site_show(self, object_id=None):
        try:
            temat = Tematy.objects.get(Q(pk=object_id), Q(nadawca=self.game.user) | Q(odbiorca=self.game.user))
            if self.game.user == temat.odbiorca:
                temat.o_prz = 'T'
            elif self.game.user == temat.nadawca:
                temat.n_prz = 'T'
            if not temat.data:
                temat.data = strftime("%Y-%m-%d %H:%M:%S")
            temat.save(force_update=True)
            if "text" in self.request.REQUEST:
                text = self.request.REQUEST['text']
                new = Wiadomosci.objects.create(temat=temat, tekst=text, kto=self.game.user,
                                                data=strftime("%Y-%m-%d %H:%M:%S"))

                alien_userprofile = None
                if self.game.user == temat.odbiorca:
                    temat.n_prz = 'N'
                    temat.n_del = 'N'
                    alien_user, alien_userprofile = self.game.lock_alien_user(temat.nadawca_id)
                elif self.request.user == temat.nadawca:
                    temat.o_prz = 'N'
                    temat.o_del = 'N'
                    alien_user, alien_userprofile = self.game.lock_alien_user(temat.odbiorca_id)
                temat.data = new.data
                temat.save(force_update=True)
                if alien_userprofile:
                    alien_userprofile.new_message += 1
                    alien_userprofile.save(force_update=True)
            wiadomosci = Wiadomosci.objects.filter(temat=temat).order_by("data")
        except Tematy.DoesNotExist:
            return HttpResponseRedirect("/game/overview/")

        topnav = topnav_site(self.game)
        return {"topnav": topnav, "temat": temat, "wiadomosci": wiadomosci}

    def site_compose(self, object_id=None):
        topnav = topnav_site(self.game)
        #try:
        user = None

        if "nick" in self.request.REQUEST:
            object_id = self.request.REQUEST['nick']
            try:
                user = User.objects.get(username__exact=object_id)
            except User.DoesNotExist:
                pass
        else:
            try:
                user = User.objects.exclude(pk=self.game.user.pk).get(pk=object_id)
            except User.DoesNotExist:
                pass
        if not user:
            self.game.send_message("Błędny odbiorca wiadomości")
            return HttpResponseRedirect(url(self.urls.list))
        alien_user, alien_userprofile = self.game.lock_alien_user(user.pk)

        errors = []
        if self.request.method == 'POST':

            if 'temat' not in self.request.POST or not len(self.request.POST['temat']) > 0:
                errors.append("Tytuł wiadomości jest wymagany!!!")
            if ('wiadomosc' not in self.request.POST) or not len(self.request.POST['wiadomosc']) > 0:
                errors.append("Treść wiadomości jest wymagana!!!")
            if not errors:
                new_t = Tematy.objects.create(nadawca=self.game.user, odbiorca=alien_user, n_del='N', o_del='N',
                                              n_prz='T', o_prz='N', temat=self.request.POST['temat'],
                                              data=strftime("%Y-%m-%d %H:%M:%S"))
                Wiadomosci.objects.create(temat=new_t, tekst=self.request.POST['wiadomosc'], kto=self.game.user,
                                          data=strftime("%Y-%m-%d %H:%M:%S"))
                self.request.session['msg'] = "Wiadomość została wysłana"
                alien_userprofile.new_message += 1
                alien_userprofile.save(force_update=True)
                return HttpResponseRedirect(url(self.urls.show, object_id=new_t.id))
        chars = string.letters + string.digits
        ticket1 = ''.join([random.choice(chars) for _ in range(16)])
        ticket2 = ''.join([random.choice(chars) for _ in range(16)])
        ktory = random.randint(0, 1)
        self.request.session['ticket1'] = ticket1
        self.request.session['ticket2'] = ticket2
        self.request.session['ktory'] = ktory
        return {"dane1": ticket1, "dane2": ticket2, "ktory": ktory, "errors": errors, "alien_user": alien_user,
                "topnav": topnav, "req": self.request.REQUEST}

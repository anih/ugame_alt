# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import force_escape, striptags

from ugame.forms.forms import SojuszForm, UprawnieniaForm, ZaproszenieForm
from ugame.models import send_error_message, send_info_message
from ugame.models.all import Czlonkowie, Sojusz, SojuszChat, SojuszLog, Zaproszenia
from ugame.topnav import topnav_site
from utils.jinja.filters import url
from ..generic.cms_metaclass import CmsMetaclass


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        sojusz_uzytkownika = self.game.get_sojusz()
        if sojusz_uzytkownika:
            return HttpResponseRedirect(url(self.urls.my))

        topnav = topnav_site(self.game)
        zaproszenia = self.game.user.zaproszenia_set.order_by("data")
        return {
            "topnav": topnav,
            "zaproszenia": zaproszenia,
        }

    site_main.url = "^ugame/alliance/$"

    def site_my(self):
        sojusz_uzytkownika = self.game.get_sojusz()
        if not sojusz_uzytkownika:
            return HttpResponseRedirect(url(self.urls.main))

        topnav = topnav_site(self.game)
        zaproszenia = self.game.user.zaproszenia_set.order_by("data")
        return {
            "topnav": topnav, "sojusz": sojusz_uzytkownika,
            "zaproszenia": zaproszenia,
        }

    def site_chat_send(self):
        user = self.user
        try:
            sojusz = user.czlonkowie.sojusz
        except:
            return HttpResponse("ERROR")
        wiadomosc = self.request.REQUEST.get("msg", None)
        if wiadomosc:
            if len(wiadomosc) > 0:
                SojuszChat.objects.create(user=user, sojusz=sojusz, wiadomosc=wiadomosc)
        return HttpResponse("OK")

    def site_chat_get(self):
        user = self.user
        last_id = self.request.REQUEST.get("id", 0)
        try:
            sojusz = user.czlonkowie.sojusz
        except Sojusz.DoesNotExist:
            return {"rows": [{"user": "Error", "wiadomosc": "Nie jesteś w sojuszu"}]}

        if not last_id > 0:
            count = SojuszChat.objects.filter(sojusz=sojusz, id__gt=last_id).count() - 20
            if count < 0:
                count = 0
            wiadomosci = SojuszChat.objects.filter(sojusz=sojusz)[count:]
        else:
            wiadomosci = SojuszChat.objects.filter(sojusz=sojusz, id__gt=last_id)
        rows = []
        for w in wiadomosci:
            rows.append({"id": w.pk, "user": w.user.username, "wiadomosc": force_escape(striptags(w.wiadomosc))})

        return {"rows": rows}

    site_chat_get.result_type = "json"

    def site_chat(self):
        sojusz_uzytkownika = self.game.get_sojusz()
        topnav = topnav_site(self.game)
        return {"topnav": topnav, "sojusz": sojusz_uzytkownika}

    def site_dolacz(self, object_id=None):
        sojusz_uzytkownika = self.game.get_sojusz()
        if sojusz_uzytkownika:
            self.game.send_message("Należysz już do sojuszu")
            return HttpResponseRedirect(url(self.urls.main))

        zaproszenia = self.game.user.zaproszenia_set.order_by("data")
        try:
            sojusz = Sojusz.objects.get(pk=object_id)
            zaproszenie_obj = self.game.user.zaproszenia_set.get(sojusz=sojusz)
        except:
            self.game.send_message("Nie masz zaproszenia do sojuszu")
            return HttpResponseRedirect(url(self.urls.main))

        self.game.send_message('Dołączyłeś do sojuszu: %s' % (sojusz.nazwa,))
        new = Czlonkowie.objects.create(user=self.game.user, sojusz=sojusz)
        tekst = "<a href='/game/usr/%s/'>%s</a> przyjął zaproszenie do sojuszu." % (
            self.game.user.pk, self.game.user.username,)
        SojuszLog.objects.create(sojusz=sojusz, tekst=tekst)
        zaproszenie_obj.delete()
        return HttpResponseRedirect(url(self.urls.main))

    def site_opusc(self):
        sojusz_uzytkownika = self.game.get_sojusz()
        if not sojusz_uzytkownika:
            return HttpResponseRedirect(url(self.urls.main))

        nalezy = self.game.get_sojusz_czlonek()

        if nalezy.wlasciciel and Czlonkowie.objects.filter(sojusz=sojusz_uzytkownika, wlasciciel=True).count() <= 1:
            sojusz_uzytkownika.zaproszenia_set.all().delete()
            sojusz_uzytkownika.czlonkowie_set.all().delete()
            sojusz_uzytkownika.sojuszlog_set.all().delete()
            sojusz_uzytkownika.sojuszchat_set.all().delete()
            sojusz_uzytkownika.delete()
            nalezy.delete()
        else:
            nalezy.delete()
            # except:pass

        send_info_message(user=self.game.user, message='Opuściłeś sojusz: %s' % (sojusz_uzytkownika.nazwa,))
        return HttpResponseRedirect(url(self.urls.main))

    def site_odrzuc(self, object_id=None):
        try:
            zaproszenie = self.game.user.zaproszenia_set.get(pk=object_id)
            sojusz = zaproszenie.sojusz
            SojuszLog.objects.create(sojusz=sojusz, tekst="<a href='/game/usr/" + str(
                self.game.user.pk) + "/'>" + self.game.user.username + '</a> odrzucił zaproszenie do sojuszu.' + "</a>")
            zaproszenie.delete()
            message = 'Odrzuciłeś zaproszenie do sojusz: %s' % (sojusz.nazwa,)
            send_error_message(user=self.user, message=message)
        except:
            sojusz = None
        return HttpResponseRedirect(url(self.urls.main))

    def site_uprawnienia(self, object_id):
        try:
            czlonek = Czlonkowie.objects.get(user=object_id)
        except:
            raise Http404

        sojusz_uzytkownika = self.game.get_sojusz()
        sojusz_czlonek = self.game.get_sojusz_czlonek()
        if not sojusz_uzytkownika:
            raise Http404

        if self.game.soj_czy_zalozyciel():
            if self.request.method == 'POST':
                form = UprawnieniaForm(data=self.request.REQUEST, instance=czlonek)
                if form.is_valid():
                    new = form.save()
                    if not Czlonkowie.objects.filter(sojusz=sojusz_uzytkownika, wlasciciel=True).count() > 0:
                        new.wlasciciel = True
                        new.save()
                        self.game.send_message("Uprawnienia zostały zmienione")
                    self.game.send_message("Uprawnienia zostały zmienione")
            else:
                form = UprawnieniaForm(instance=czlonek)

            return {"form": form, "id": czlonek.user_id}
        else:
            self.game.send_message("Nie masz uprawnień")
            return {}

    def site_wyslij_zaproszenie(self, object_id=None):
        try:
            zapraszany = User.objects.get(pk=object_id)
        except:
            raise Http404

        sojusz_uzytkownika = self.game.get_sojusz()
        if not sojusz_uzytkownika:
            return HttpResponseRedirect(url(self.urls.main))

        if not self.game.soj_czy_moze_zapraszac():
            self.game.send_message("Nie możesz zapraszać")
            return HttpResponseRedirect(url(self.urls.zaproszenia))
        elif self.game.soj_czy_nie_nalezy(zapraszany, sojusz_uzytkownika) and self.game.soj_czy_nie_zaproszony(
                zapraszany, sojusz_uzytkownika):
            zaproszenie_obj = Zaproszenia(user=zapraszany, sojusz=sojusz_uzytkownika, od=self.game.user)
            if self.request.method == 'POST':
                form = ZaproszenieForm(data=self.request.REQUEST, instance=zaproszenie_obj)
                if form.is_valid():
                    form.save()
                    self.game.send_message("Zaproszenie zostało wysłane")
                    SojuszLog.objects.create(sojusz=sojusz_uzytkownika, tekst='Gracz ' + "<a href='/game/usr/" + str(
                        zapraszany.pk) + "/'>" + zapraszany.username + '</a> został zaproszony przez gracza ' + "<a "
                                                                                                                "href='/game/usr/" + str(
                        self.game.user.pk) + "/'>" + self.game.user.username + "</a>")
                    return HttpResponseRedirect(url(self.urls.zaproszenia))
            else:
                form = ZaproszenieForm(instance=zaproszenie_obj)

            topnav = topnav_site(self.game)
            return {"topnav": topnav, "form": form, "zapraszany": zapraszany}
        else:
            self.game.send_message("Użytkownik już był zapraszany lub jest w plemieniu")
        return HttpResponseRedirect(url(self.urls.zaproszenia))

    def site_zaproszenia(self):
        sojusz_uzytkownika = self.game.get_sojusz()
        if not sojusz_uzytkownika:
            return HttpResponseRedirect(url(self.urls.main))

        if self.request.REQUEST.has_key("del") and self.game.soj_czy_moze_zapraszac():
            sojusz_uzytkownika.zaproszenia_set.filter(pk=self.request.REQUEST['del']).delete()
        zaproszenia = sojusz_uzytkownika.zaproszenia_set.order_by("data")

        if self.request.REQUEST.has_key("nick"):
            try:
                zapraszany = User.objects.get(username=self.request.REQUEST['nick'])
                sojusz_mozesz = self.game.soj_czy_moze_zapraszac()
                if not sojusz_mozesz:
                    self.game.send_message('Nie masz uprawnień do zapraszania')
                    return HttpResponseRedirect(url(self.urls.zaproszenia))
                return HttpResponseRedirect(url(self.urls.wyslij_zaproszenie, object_id=zapraszany.id))

            except User.DoesNotExist:
                self.game.send_message('Nie ma takiego gracza')
                return HttpResponseRedirect(url(self.urls.zaproszenia))

        topnav = topnav_site(self.game)
        return {"topnav": topnav, "zaproszenia": zaproszenia, "self.game": self.game}

    def site_czlonkowie(self):
        sojusz_uzytkownika = self.game.get_sojusz()
        if not sojusz_uzytkownika:
            return HttpResponseRedirect(url(self.urls.main))

        czlonek_sojusz = self.game.get_sojusz_czlonek()

        if self.request.REQUEST.has_key("del") and self.game.soj_czy_moze_wyrzucac():
            if Czlonkowie.objects.select_for_update().filter(sojusz=sojusz_uzytkownika,
                                                             pk=self.request.REQUEST['del']).count() > 0:
                czlonek = Czlonkowie.objects.select_for_update().get(sojusz=sojusz_uzytkownika,
                                                                     pk=self.request.REQUEST['del'])
                if not czlonek.wlasciciel:
                    czlonek.delete()
                else:
                    ile_wlascicieli = Czlonkowie.objects.filter(sojusz=sojusz_uzytkownika, wlasciciel=True).count()
                    if czlonek_sojusz.wlasciciel and ile_wlascicieli >= 2:
                        czlonek.delete()

        czlonkowie = sojusz_uzytkownika.czlonkowie_set.order_by("data")
        print sojusz_uzytkownika.nazwa, self.game.soj_czy_zalozyciel()
        topnav = topnav_site(self.game)
        return {"topnav": topnav, "czlonkowie": czlonkowie, "self.game": self.game, }

    def site_przeglad(self):
        sojusz_uzytkownika = self.game.get_sojusz()
        if not sojusz_uzytkownika:
            return HttpResponseRedirect(url(self.urls.main))

        wydarzenia = sojusz_uzytkownika.sojuszlog_set.order_by("-id")
        topnav = topnav_site(self.game)
        return {"topnav": topnav, "sojusz": sojusz_uzytkownika, "wydarzenia": wydarzenia}

    def site_zaloz(self):
        if Czlonkowie.objects.select_for_update().filter(user=self.game.user).count() > 0 > 0:
            return HttpResponseRedirect(url(self.urls.main))

        if self.request.method == 'POST':
            form = SojuszForm(self.request.POST, self.request.FILES)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.save()  # tu tak ma byc
                czlonek = Czlonkowie.objects.create(user=self.game.user, sojusz=obj, wlasciciel=True)
                SojuszLog.objects.create(sojusz=obj,
                                         tekst='Sojuszu został założony przez ' + "<a href='/game/usr/" + str(
                                             self.game.user.pk) + "/'>" + self.game.user.username + "</a>")
                return HttpResponseRedirect(url(self.urls.profil))
        else:
            form = SojuszForm()

        topnav = topnav_site(self.game)
        return {"topnav": topnav, "form": form}

    def site_profil_edytuj(self):
        sojusz_uzytkownika = self.game.get_sojusz()
        if not sojusz_uzytkownika:
            return HttpResponseRedirect(url(self.urls.main))

        if not self.game.soj_czy_moze_edytowac_opis():
            self.game.send_message("Nie masz uprawnień do edycji opisu sojuszu")
            return HttpResponseRedirect(url(self.urls.profil))

        if self.request.method == 'POST':
            form = SojuszForm(self.request.POST, self.request.FILES, instance=sojusz_uzytkownika)
            if form.is_valid():
                obj = form.save(commit=False)
                if not obj.avatar:
                    obj.avatar = sojusz_uzytkownika.avatar
                obj.save()  # tu tak ma byc
                self.game.send_message("Opis sojuszu został zapisany")
                return HttpResponseRedirect(url(self.urls.my))
        else:
            form = SojuszForm(instance=sojusz_uzytkownika)
        topnav = topnav_site(self.game)
        return {"topnav": topnav, "form": form, "self.game": self.game}

    def site_show(self, object_id):
        try:
            sojusz = Sojusz.objects.get(pk=object_id)
        except:
            self.game.send_message("Nie ma takiego sojuszu")
            return HttpResponseRedirect(url(self.urls.main))
        czlonkowie = sojusz.czlonkowie_set.order_by("data")
        topnav = topnav_site(self.game)
        return {"topnav": topnav, "sojusz": sojusz, "czlonkowie": czlonkowie}

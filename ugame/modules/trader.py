# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from math import ceil, floor

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect

from ugame.forms.forms import RynekForm, RynekSearch
from ugame.funkcje import Output
from ugame.klasy.BaseGame import BaseGame
from ugame.models import send_error_message, send_info_message
from ugame.models.all import Rynek
from ugame.topnav import topnav_site
from utils.jinja.filters import url
from ..generic.cms_metaclass import CmsMetaclass

dlugie_nazwy = {
    "m": "metalu",
    "k": "kryształu",
    "d": "deuteru"
}

grid_sprzedawcy = {
    "m": {"m": 100 / 100, "k": 60 / 100, "d": 30 / 100},
    "k": {"m": 100 / 60, "k": 60 / 60, "d": 30 / 60},
    "d": {"m": 100 / 30, "k": 60 / 30, "d": 30 / 30},
}


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self, page=1):
        # current_planet = self.game.get_current_planet()
        sort_form = RynekSearch(self.request.POST, prefix="sortowanie_surowiec")

        # rynek = Rynek.objects.exclude(planeta__owner=user).order_by("ratio")
        rynek = Rynek.objects.order_by("ratio")

        sortowanie_surowiec_co = None
        if 'handlarz_sort_surowiec_co' in self.request.session:
            sortowanie_surowiec_co = self.request.session['handlarz_sort_surowiec_co']

        sortowanie_surowiec_na = None
        if 'handlarz_sort_surowiec_na' in self.request.session:
            sortowanie_surowiec_na = self.request.session['handlarz_sort_surowiec_na']

        try:
            page = int(page)
            if page <= 0:
                page = 1
        except:
            page = 1

        if sort_form.is_valid():
            if sort_form.cleaned_data['co'] in ('M', 'K', 'D'):
                sortowanie_surowiec_co = sort_form.cleaned_data['co']
            elif sort_form.cleaned_data['co'] == '-':
                sortowanie_surowiec_co = None
            else:
                sort_form.cleaned_data['co'] = sortowanie_surowiec_co

            if sort_form.cleaned_data['na'] in ('M', 'K', 'D'):
                sortowanie_surowiec_na = sort_form.cleaned_data['na']
            elif sort_form.cleaned_data['na'] == '-':
                sortowanie_surowiec_na = None
            else:
                sort_form.cleaned_data['na'] = sortowanie_surowiec_na

            self.request.session['handlarz_sort_surowiec_co'] = sortowanie_surowiec_co
            self.request.session['handlarz_sort_surowiec_na'] = sortowanie_surowiec_na

        if sortowanie_surowiec_co:
            print "zmiana co na:", sortowanie_surowiec_co
            rynek = rynek.filter(co=sortowanie_surowiec_co)

        if sortowanie_surowiec_na:
            print "zmiana na na:", sortowanie_surowiec_na
            rynek = rynek.filter(na=sortowanie_surowiec_na)

        paginator = Paginator(rynek, 20, allow_empty_first_page=True)
        try:
            p = paginator.page(page)
        except:
            return HttpResponseRedirect(url(self.url))

        rynek_obj = p.object_list

        topnav = topnav_site(self.game)
        return {
            "topnav": topnav, "rynek": rynek_obj,
            "sort_form": sort_form, "paginator": paginator,
            "page": page, "page_list": p,
        }

    site_main.url = "^ugame/trader/{r}$"

    def site_for_sale(self, page=1):
        try:
            page = int(page)
            if page <= 0:
                page = 1
        except:
            page = 1
        current_planet = self.game.get_current_planet()

        rynek_obj = Rynek(planeta=current_planet)

        if self.request.method == 'POST':
            rynek_form = RynekForm(instance=rynek_obj, data=self.request.POST)
            if rynek_form.is_valid():
                co = rynek_form.cleaned_data['co']
                co_ile = rynek_form.cleaned_data['co_ile']
                # na = rynek_form.cleaned_data['na']
                na_ile = rynek_form.cleaned_data['na_ile']
                ilosc = rynek_form.cleaned_data['ilosc']
                dobre_dane = True
                ile_surowca = int(ceil(co_ile * ilosc * 1.05))

                if na_ile / co_ile > 100.0 or na_ile / co_ile < 0.01:
                    message = "Stosunek kupna do sprzedaży musi zawierać sie od 100/1 do 1/100"
                    send_error_message(user=self.game.user, message=message)
                    dobre_dane = False

                if co_ile < 0 or na_ile < 0:
                    message = "Wartości muszą być większe od 0"
                    send_error_message(user=self.game.user, message=message)
                    dobre_dane = False

                if dobre_dane:
                    if co == 'M':
                        if ile_surowca > current_planet.metal:
                            message = "Nie masz tyle metalu na planecie: %s" % ile_surowca
                            send_error_message(user=self.game.user, message=message)
                            dobre_dane = False
                        else:
                            current_planet.metal -= ile_surowca
                    elif co == 'K':
                        if ile_surowca > current_planet.crystal:
                            message = "Nie masz tyle kryształu na planecie: %s" % ile_surowca
                            send_error_message(user=self.game.user, message=message)
                            dobre_dane = False
                        else:
                            current_planet.crystal -= ile_surowca
                    elif co == 'D':
                        if ile_surowca > current_planet.deuter:
                            message = "Nie masz tyle deuteru na planecie: %s" % ile_surowca
                            send_error_message(user=self.game.user, message=message)
                            dobre_dane = False
                        else:
                            current_planet.deuter -= ile_surowca

                if Rynek.objects.select_for_update().filter(planeta__owner=self.game.user).count() > 15:
                    message = "Osiągnąłeś limit 15 ofert na rynku, nie możesz już więcej wystawić"
                    send_error_message(user=self.game.user, message=message)
                    dobre_dane = False

                if dobre_dane:
                    rynek_obj = rynek_form.save(commit=False)
                    rynek_obj.planeta = current_planet
                    rynek_obj.ratio = na_ile / co_ile
                    rynek_obj.save()  # tu tak ma byc
                    message = "Wystawiłeś ofertę na rynku"
                    send_info_message(user=self.game.user, message=message)
                    return HttpResponseRedirect(url(self.urls.main))
            else:
                message = "Musisz podać wszystkie dane"
                send_error_message(user=self.game.user, message=message)
        else:
            rynek_form = RynekForm(instance=rynek_obj)

        if "wycofaj" in self.request.GET:
            try:
                wycofanie = Rynek.objects.select_for_update().get(pk=self.request.GET['wycofaj'],
                                                                  planeta__owner=self.game.user)
                planeta_wycofania = self.game.get_planet(wycofanie.planeta_id)

                ile_surowca = int(wycofanie.co_ile * wycofanie.ilosc)
                if wycofanie.co == 'M':
                    message = "Wycofanie oferty, przybyło metalu na planecie: %s" % ile_surowca
                    send_info_message(user=self.game.user, message=message)
                    planeta_wycofania.metal += ile_surowca
                elif wycofanie.co == 'K':
                    message = "Wycofanie oferty, przybyło kryształu na planecie: %s" % ile_surowca
                    send_info_message(user=self.game.user, message=message)
                    planeta_wycofania.crystal += ile_surowca
                elif wycofanie.co == 'D':
                    message = "Wycofanie oferty, przybyło deuteru na planecie: %s" % ile_surowca
                    send_info_message(user=self.game.user, message=message)
                    planeta_wycofania.deuter += ile_surowca
                wycofanie.delete()
                return HttpResponseRedirect(url(self.url))

            except:
                return HttpResponseRedirect(url(self.url))

        rynek_twoje = Rynek.objects.filter(planeta__owner=self.game.user)
        paginator = Paginator(rynek_twoje, 20, allow_empty_first_page=True)
        try:
            p = paginator.page(page)
        except:
            return HttpResponseRedirect(url(self.url))

        rynek_obj = p.object_list

        topnav = topnav_site(self.game)
        return {
            "topnav": topnav, "rynek_twoje": rynek_obj,
            "rynek_form": rynek_form, "paginator": paginator,
            "page": page, "page_list": p,
        }

    def site_take_offer(self):
        current_planet = self.game.get_current_planet()

        if "id" in self.request.REQUEST:
            try:
                rynek_obj = Rynek.objects.select_for_update().get(pk=self.request.REQUEST['id'])
                req_obj = Output()
                req_obj.user = rynek_obj.planeta.owner
                GraAlienObject = BaseGame(req_obj)
                GraAlienObject.save_all()
                planeta_alien = GraAlienObject.get_planet(rynek_obj.planeta_id)
                rynek_obj = Rynek.objects.select_for_update().get(pk=self.request.REQUEST['id'])
            except Rynek.DoesNotExist:
                message = "Nie ma już takiej oferty na rynku, wybież inną"
                send_error_message(user=self.game.user, message=message)
                return HttpResponseRedirect(url(self.urls.main))
        else:
            message = "Nie ma już takiej oferty na rynku, wybież inną"
            send_error_message(user=self.game.user, message=message)
            return HttpResponseRedirect(url(self.urls.main))

        if rynek_obj.planeta.owner_id == self.game.user.id:
            message = "Nie możesz kupić swojej oferty, nawet jeśli jest z innej planety"
            send_error_message(user=self.game.user, message=message)
            GraAlienObject.save_all()
            return HttpResponseRedirect(url(self.urls.main))

        try:
            ilosc = int(self.request.REQUEST["ilosc"])
        except:
            send_error_message(user=self.game.user, message="Wybież prawidłową ilość paczek")
            GraAlienObject.save_all()
            return HttpResponseRedirect(url(self.urls.main))

        if ilosc > rynek_obj.ilosc:
            message = "Wybież prawidłową ilość paczek"
            send_error_message(user=self.game.user, message=message)
            GraAlienObject.save_all()
            return HttpResponseRedirect(url(self.urls.main))

        ile_oddajemy = ilosc * rynek_obj.na_ile

        if rynek_obj.na == 'M':
            if ile_oddajemy > current_planet.metal:
                message="Nie masz tyle surowców żeby to kupić"
                send_error_message(user=self.game.user, message=message)
                GraAlienObject.save_all()
                return HttpResponseRedirect(url(self.urls.main))
            current_planet.metal -= ile_oddajemy
            planeta_alien.metal += ile_oddajemy

        elif rynek_obj.na == 'K':
            if ile_oddajemy > current_planet.crystal:
                message="Nie masz tyle surowców żeby to kupić"
                send_error_message(user=self.game.user, message=message)
                GraAlienObject.save_all()
                return HttpResponseRedirect(url(self.urls.main))
            current_planet.crystal -= ile_oddajemy
            planeta_alien.crystal += ile_oddajemy

        elif rynek_obj.na == 'D':
            if ile_oddajemy > current_planet.deuter:
                message="Nie masz tyle surowców żeby to kupić"
                send_error_message(user=self.game.user, message=message)
                GraAlienObject.save_all()
                return HttpResponseRedirect(url(self.urls.main))
            current_planet.deuter -= ile_oddajemy
            planeta_alien.deuter += ile_oddajemy

        message = "%s kupił %s paczek po %s %s" % (
            self.game.user.username, ilosc,
            rynek_obj.na_ile, dlugie_nazwy[str(rynek_obj.na).lower()]
        )
        send_info_message(user=GraAlienObject.user, message=message)
        ile_dostajemy = rynek_obj.co_ile * ilosc
        if rynek_obj.co == 'M':
            current_planet.metal += ile_dostajemy
        elif rynek_obj.co == 'K':
            current_planet.crystal += ile_dostajemy
        elif rynek_obj.co == 'D':
            current_planet.deuter += ile_dostajemy

        if ilosc >= rynek_obj.ilosc:
            rynek_obj.delete()
        else:
            rynek_obj.ilosc -= ilosc
            rynek_obj.save(force_update=True)

        message = "Właśnie kupiłeś surowce"
        send_info_message(user=self.game.user, message=message)

        GraAlienObject.save_all()

        return HttpResponseRedirect(url(self.urls.main))

    def site_dealer(self):
        topnav = topnav_site(self.game)

        return {
            "topnav": topnav,
        }

    def site_take_from_dealer(self):
        planeta = self.game.get_current_planet()
        poprawne_dane = True

        if 'co_sprzedaje' not in self.request.POST:
            message="Musisz wybrać co sprzedajesz"
            send_error_message(user=self.game.user, message=message)
            poprawne_dane = False
        else:
            co_sprzedaje = self.request.POST['co_sprzedaje']
            if co_sprzedaje not in ('m', 'k', 'd'):
                message="Musisz wybrać co sprzedajesz"
                send_error_message(user=self.game.user, message=message)
                poprawne_dane = False

        if 'sprzedaje_na' not in self.request.POST:
            message="Musisz wybrać co kupujesz"
            send_error_message(user=self.game.user, message=message)
            poprawne_dane = False
        else:
            sprzedaje_na = self.request.POST['sprzedaje_na']
            if sprzedaje_na not in ('m', 'k', 'd'):
                message="Musisz wybrać co kupujesz"
                send_error_message(user=self.game.user, message=message)
                poprawne_dane = False
        try:
            ilosc_sprzedawanego = int(self.request.POST['ilosc_sprzedawanego'])
        except:
            message="Musisz podać poprawną ilość sprzedawanego surowca"
            send_error_message(user=self.game.user, message=message)
            poprawne_dane = False

        if poprawne_dane:
            ile_mam = 0
            if co_sprzedaje == 'm':
                ile_mam = planeta.metal
            elif co_sprzedaje == 'k':
                ile_mam = planeta.crystal
            elif co_sprzedaje == 'd':
                ile_mam = planeta.deuter

            if ilosc_sprzedawanego < 0:
                message="Ilość sprzedawanego musi być większa od 0"
                send_error_message(user=self.game.user, message=message)
                poprawne_dane = False
            elif ile_mam < ilosc_sprzedawanego:
                message="Nie masz tyle surowca"
                send_error_message(user=self.game.user, message=message)
                poprawne_dane = False
            else:
                ile_kupilismy = floor(floor(ilosc_sprzedawanego * 0.9) * grid_sprzedawcy[co_sprzedaje][sprzedaje_na])
                if co_sprzedaje == 'm':
                    planeta.metal -= ilosc_sprzedawanego
                elif co_sprzedaje == 'k':
                    planeta.crystal -= ilosc_sprzedawanego
                elif co_sprzedaje == 'd':
                    planeta.deuter -= ilosc_sprzedawanego

                if sprzedaje_na == 'm':
                    planeta.metal += ile_kupilismy
                elif sprzedaje_na == 'k':
                    planeta.crystal += ile_kupilismy
                elif sprzedaje_na == 'd':
                    planeta.deuter += ile_kupilismy
                message="Kupiłeś %s %s za %s %s" % (
                    int(ile_kupilismy), dlugie_nazwy[sprzedaje_na], ilosc_sprzedawanego, dlugie_nazwy[co_sprzedaje])
                send_info_message(user=self.game.user, message=message)
        return HttpResponseRedirect(url(self.urls.dealer))

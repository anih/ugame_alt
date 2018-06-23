# -*- coding: utf-8 -*-
from time import time
from django.http import HttpResponseRedirect

from ugame.models import send_error_message
from ...generic.cms_metaclass import CmsMetaclass
from settings import FLEET_SPEED
from ugame.klasy.BaseGame import Output
from ugame.topnav import topnav_site
from ugame.models.all import Flota_p, Galaxy, Fleets
from ugame.funkcje import get_speed, check_is_planet, is_planet_owner, get_ship_request, check_ship_request, \
    odleglosc, getCzasLotu, get_zuzycie_deuteru


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_choose(self):
        current_planet = self.game.get_current_planet()

        dane = Output()
        try:
            dane.planeta_id = int(self.request.REQUEST['p'])
            dane.system_id = int(self.request.REQUEST['s'])
            dane.galaktyka_id = int(self.request.REQUEST['g'])
            if 'ship_request' in self.request.session:
                del self.request.session['ship_request']
        except:
            if 'planeta_dane' in self.request.session:
                dane = self.request.session['planeta_dane']
            else:

                return HttpResponseRedirect("/game/galaxy/")
        if not check_is_planet(self.game.user, dane.planeta_id, dane.system_id, dane.galaktyka_id):
            return HttpResponseRedirect("/game/galaxy/")
        if 'ship_request' in self.request.session:
            ship_request = self.request.session['ship_request']
            if not self.request.REQUEST.has_key("cp"):
                del self.request.session['ship_request']
        else:
            ship_request = None

        if is_planet_owner(self.game.user, dane, True):
            return HttpResponseRedirect("/game/galaxy/")

        topnav = topnav_site(self.game)

        dostepne_statki_tmp = Flota_p.objects.values_list('budynek_id', flat=True).filter(planeta=current_planet,
                                                                                          budynek__lata__gt=0,
                                                                                          ilosc__gt=0).order_by(
            "budynek")
        dostepne_statki = []
        for i in dostepne_statki_tmp:
            d = Output()
            statek = self.game.cache_obj.get_flota_p(current_planet.pk, i)
            d.nazwa = statek.budynek.nazwa
            d.ilosc = statek.ilosc
            d.pk = statek.pk
            d.speed = int(get_speed(self.game, statek.budynek, self.game.user))
            if ship_request:
                try:
                    d.value = int(ship_request[d.statek.budynek_id])
                except:
                    d.value = 0
            else:
                d.value = 0
            dostepne_statki.append(d)

        self.request.session['planeta_dane'] = dane
        return {"dane": dane, 'topnav': topnav, "dostepne_statki": dostepne_statki}

    def site_accept(self):
        current_planet = self.game.get_current_planet()

        if 'planeta_dane' in self.request.session:
            planeta_dane = self.request.session['planeta_dane']
        else:

            return HttpResponseRedirect("/game/overview/")

        try:
            if self.request.REQUEST.has_key('speed'):
                test = float(self.request.REQUEST['speed'])
                planeta_dane.speed_procent = test
            if not planeta_dane.speed_procent >= 1.0 or not planeta_dane.speed_procent <= 10.0:
                planeta_dane.speed_procent = 10.0
        except:

            return HttpResponseRedirect("/game/fs/atak/")

        if not check_is_planet(self.game.user, planeta_dane.planeta_id, planeta_dane.system_id,
                               planeta_dane.galaktyka_id):
            return HttpResponseRedirect("/game/galaxy/")

        if is_planet_owner(self.game.user, planeta_dane, True):
            return HttpResponseRedirect("/game/galaxy/")

        if 'id_statkow' in self.request.session:
            id_statkow = self.request.session['id_statkow']
        else:
            id_statkow = None
        if 'ship_request' in self.request.session:
            ship_request = self.request.session['ship_request']
        else:
            ship_request = None

        if not id_statkow or not ship_request:
            tmp = get_ship_request(self.game, current_planet, self.request, self.game.user, planeta_dane)
        else:
            tmp = get_ship_request(self.game, current_planet, self.request, self.game.user, planeta_dane, False, False,
                                   False)

        if not tmp:
            if not id_statkow or not ship_request:

                return HttpResponseRedirect("/game/fs/atak/")
            else:
                tmp = check_ship_request(self.game, self.request, current_planet, planeta_dane, id_statkow,
                                         ship_request,
                                         self.game.user)
                if not tmp:
                    return HttpResponseRedirect("/game/fs/atak/")

        id_statkow = tmp['id_statkow']
        ship_request = tmp['ship_request']
        dane_floty = tmp['dane_floty']
        statki_podsumowanie = tmp['statki_podsumowanie']

        dane_floty.odleglosc = odleglosc(current_planet, planeta_dane.galaktyka_id, planeta_dane.system_id,
                                         planeta_dane.planeta_id)
        dane_floty.czas_lotu = getCzasLotu(planeta_dane.speed_procent, dane_floty.speed, dane_floty.odleglosc,
                                           FLEET_SPEED)
        dane_floty.zuzycie_deuter = get_zuzycie_deuteru(dane_floty, planeta_dane)

        if dane_floty.bak_pojemnosc - dane_floty.zuzycie_deuter < 0:
            message="Nie można zabrać wystarczająco paliwa. Pojemność baków:" + str(
                dane_floty.bak_pojemnosc) + ", potrzeba:" + str(dane_floty.zuzycie_deuter)
            send_error_message(user=self.game.user, message=message)

            return HttpResponseRedirect("/game/fs/atak/")
        if dane_floty.zuzycie_deuter > current_planet.deuter:
            message="Masz za mało deuteru na planecie"
            send_error_message(user=self.game.user, message=message)
            return HttpResponseRedirect("/game/fs/atak/")

        self.request.session['planeta_dane'] = planeta_dane
        self.request.session['dane_floty'] = dane_floty
        self.request.session['ship_request'] = ship_request
        self.request.session['id_statkow'] = id_statkow

        topnav = topnav_site(self.game)

        return {"planeta_dane": planeta_dane, "dane_floty": dane_floty, 'topnav': topnav,
                "statki_podsumowanie": statki_podsumowanie}

    def site_send(self):
        current_planet = self.game.get_current_planet()

        if 'planeta_dane' in self.request.session:
            planeta_dane = self.request.session['planeta_dane']
        else:

            return HttpResponseRedirect("/game/overview/")
        if 'id_statkow' in self.request.session:
            id_statkow = self.request.session['id_statkow']
        else:

            return HttpResponseRedirect("/game/overview/")
        if 'ship_request' in self.request.session:
            ship_request = self.request.session['ship_request']
        else:

            return HttpResponseRedirect("/game/overview/")

        if not check_is_planet(self.game.user, planeta_dane.planeta_id, planeta_dane.system_id,
                               planeta_dane.galaktyka_id):
            return HttpResponseRedirect("/game/galaxy/")

        if is_planet_owner(self.game.user, planeta_dane, True):
            return HttpResponseRedirect("/game/galaxy/")

        tmp = check_ship_request(self.game, self.request, current_planet, planeta_dane, id_statkow, ship_request,
                                 self.game.user)
        if not tmp:
            return HttpResponseRedirect("/game/overview/")
        dane_floty = tmp['dane_floty']
        id_statkow = tmp['id_statkow']
        ship_request = tmp['ship_request']

        dane_floty.odleglosc = odleglosc(current_planet, planeta_dane.galaktyka_id, planeta_dane.system_id,
                                         planeta_dane.planeta_id)
        dane_floty.czas_lotu = getCzasLotu(planeta_dane.speed_procent, dane_floty.speed, dane_floty.odleglosc,
                                           FLEET_SPEED)
        dane_floty.zuzycie_deuter = get_zuzycie_deuteru(dane_floty, planeta_dane)

        if dane_floty.bak_pojemnosc - dane_floty.zuzycie_deuter < 0:
            message="Nie można zabrać wystarczająco paliwa. Pojemność baków:" + str(
                dane_floty.bak_pojemnosc) + ", potrzeba:" + str(dane_floty.zuzycie_deuter)
            send_error_message(user=self.game.user, message=message)

            return HttpResponseRedirect("/game/fs/atak/")
        if dane_floty.zuzycie_deuter > current_planet.deuter:
            message="Masz za mało deuteru na planecie"
            send_error_message(user=self.game.user, message=message)
            return HttpResponseRedirect("/game/fs/atak/")

        current_planet.deuter -= dane_floty.zuzycie_deuter

        fleet_array = []
        fleet_amount = 0
        for i in id_statkow:
            fleet_array.append("%s,%s" % (i, ship_request[i]))
            fleet_amount += int(ship_request[i])
            statek_row = self.game.cache_obj.get_flota_p(current_planet.pk, int(i))
            statek_row.ilosc -= int(ship_request[i])

        time_start = time()

        galaxy_end = Galaxy.objects.get(galaxy=planeta_dane.galaktyka_id, system=planeta_dane.system_id,
                                        field=planeta_dane.planeta_id)

        flota_row = Fleets.objects.create(fleet_owner=self.game.user, fleet_mission=4, fleet_amount=fleet_amount,
                                          fleet_array=";".join(fleet_array), time_start=time_start,
                                          galaxy_start=current_planet.galaxy,
                                          time=time_start + dane_floty.czas_lotu,
                                          galaxy_end=galaxy_end,
                                          fleet_resource_metal=0, fleet_resource_crystal=0, fleet_resource_deuterium=0,
                                          bak=dane_floty.zuzycie_deuter)

        del self.request.session['id_statkow']
        del self.request.session['ship_request']
        del self.request.session['planeta_dane']

        return HttpResponseRedirect("/game/fleet/")

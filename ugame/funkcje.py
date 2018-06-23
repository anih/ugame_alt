# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from math import ceil
from math import sqrt
from string import split
from time import localtime
from time import strftime
from time import time

from django.contrib.auth.models import User

from settings import FLEET_SPEED
from settings import MAX_GALAXY
from settings import MAX_PLANETA
from settings import MAX_SYSTEM
from ugame.models import send_error_message
from ugame.models.all import Badania
from ugame.models.all import Fleets
from ugame.models.all import Flota
from ugame.models.all import Flota_p
from ugame.models.all import Galaxy
from ugame.models.all import Planets
from ugame.models.all import UserProfile


class Output: pass


def lock_user_cron(user_id, p):
    user = User.objects.select_for_update().get(pk=user_id.pk)
    userprofile = UserProfile.objects.select_for_update().get(user=user)
    planeta = Planets.objects.select_for_update().get(pk=p.pk)
    return user, userprofile, planeta


def lock_user(request):
    user = User.objects.select_for_update().get(pk=request.user.pk)
    userprofile = UserProfile.objects.select_for_update().get(user=user)
    change_planet(request, user, userprofile)
    if Planets.objects.filter(pk=userprofile.current_planet_id).count() > 0:
        planeta = Planets.objects.select_for_update().get(pk=userprofile.current_planet_id)
    else:
        userprofile.current_planet = Planets.objects.filter(owner=user)[0]
        userprofile.save(force_update=True)
        planeta = Planets.objects.select_for_update().get(pk=userprofile.current_planet)

    return user, planeta, userprofile


def change_planet(request, user, userprofile):
    try:
        if int(request.REQUEST['cp']) > 0:
            if user.planets_set.filter(pk=request.REQUEST['cp']).count() > 0:
                planeta_nowa = user.planets_set.get(pk=request.REQUEST['cp'])
                userprofile.current_planet = planeta_nowa
                userprofile.save(force_update=True)
    except:
        pass


def zawroc(flota, user):
    if Fleets.objects.select_for_update().filter(pk=flota, fleet_owner=user, fleet_back__lt=1).count() > 0:
        try:
            flota = Fleets.objects.select_for_update().get(pk=flota, fleet_owner=user, fleet_back__lt=1)
            czas_teraz = int(time())
            lot_trwa = czas_teraz - flota.time_start
            caly_lot_czas = flota.time - flota.time_start

            procent_lotu = float(lot_trwa) / float(caly_lot_czas) / 2
            bak_zostanie = flota.bak - (flota.bak * procent_lotu)

            flota.bak = bak_zostanie
            flota.fleet_resource_deuterium += bak_zostanie
            galaxy_end = flota.galaxy_end

            flota.galaxy_end = flota.galaxy_start
            flota.galaxy_start = galaxy_end

            flota.time_start = int(czas_teraz)
            flota.time = int(czas_teraz + lot_trwa)
            flota.fleet_back = 1
            flota.save(force_update=True)
        except:
            message = "Wybierz poprawną flote"
            send_error_message(user=user, message=message)
    else:
        message = "Nie ma takiej floty do zawrócenia"
        send_error_message(user=user, message=message)


def get_max_field(planet):
    return planet.powierzchnia_max  # +planet.terraformer_fields*15


def pretty_time(seconds):
    day = int(seconds / (24 * 3600))
    hs = int(seconds / 3600 % 24)
    min = int(seconds / 60 % 60)
    seg = int(seconds / 1 % 60)
    time = ''
    if (day != 0):
        time += str(day) + ':'
        if (hs < 10):
            hs = "0" + str(hs)
    if (min < 10):
        min = "0" + str(min)
    time += str(hs) + ':'
    time += str(min) + ':'
    if (seg < 10):
        seg = "0" + str(seg)
    time += str(seg) + '';
    return time


def check_field_current(p):
    # TODO to sie nadaje do dupy po przerobkach/ moze jakis daemon odpalany pozno w nocy?
    return True
    cfc = 0
    cfc = p.metal_mine + p.crystal_mine + p.deuterium_sintetizer
    cfc += p.solar_plant + p.fusion_plant + p.robot_factory
    cfc += p.nano_factory + p.hangar + p.metal_store
    cfc += p.crystal_store + p.deuterium_store + p.laboratory
    cfc += p.terraformer + p.ally_deposit + p.silo
    p.field_current = cfc
    p.save(force_update=True)


def to_int(liczba):
    try:
        liczba = int(liczba)
    except:
        liczba = 0
    return liczba


def odleglosc(planeta, o_gal, o_sys, o_pla):
    o_gal = to_int(o_gal)
    o_sys = to_int(o_sys)
    o_pla = to_int(o_pla)

    if (planeta.galaxy.galaxy - o_gal) != 0:
        odl = abs(planeta.galaxy.galaxy - o_gal) * 20000
    elif (planeta.galaxy.system - o_sys) != 0:
        odl = abs(planeta.galaxy.system - o_sys) * 5 * 19 + 2700
    elif (planeta.galaxy.field - o_pla) != 0:
        odl = abs(planeta.galaxy.field - o_pla) * 5 + 1000
    else:
        odl = 5
    return odl


def getCzasLotu(game_speed, speed, distance, fleet_speed):
    from math import sqrt
    game_speed = float(game_speed)
    speed = float(speed)
    distance = float(distance)
    fleet_speed = float(fleet_speed)
    return int(round((10000 / game_speed * sqrt(distance * 10 / speed) + 10) / fleet_speed))


def get_speed(GraObject, statek, user):
    if statek.speed_bad:
        level_badania = GraObject.bad_get_level(user, statek.speed_bad_id)
        speed = statek.speed * (1 + level_badania * statek.speed_bad.speed_factor)
    else:
        speed = statek.speed
    return speed


def icon(request):
    from django import http
    from settings import MEDIA_ROOT
    f = open(MEDIA_ROOT + "img/favicon.ico")
    return http.HttpResponse(f.read(),
                             mimetype='image/x-icon')


def check_free_planet(user, planeta_id, system_id, galaktyka_id):
    if not planeta_id > 0 or planeta_id > MAX_PLANETA or not galaktyka_id > 0 or galaktyka_id > MAX_GALAXY or not \
            system_id > 0 or system_id > MAX_SYSTEM:
        message = "Niepoprawne dane dotyczące pozycji planety w systemie planetarnym"
        send_error_message(user=user, message=message)
        return False

    if Galaxy.objects.filter(galaxy=galaktyka_id, system=system_id, field=planeta_id,
                             planet__owner__isnull=False).count() > 0:
        message = "Niestety planeta " + str(galaktyka_id) + ":" + str(system_id) + ":" + str(
            planeta_id) + " jest już zajęta"
        send_error_message(user=user, message=message)
        return False
    return True


def check_is_planet(user, planeta_id, system_id, galaktyka_id):
    if not planeta_id > 0 or planeta_id > MAX_PLANETA or not galaktyka_id > 0 or galaktyka_id > MAX_GALAXY or not \
            system_id > 0 or system_id > MAX_SYSTEM:
        message = "Niepoprawne dane dotyczące pozycji planety w systemie planetarnym"
        send_error_message(user=user, message=message)
        return False
    tmp = Galaxy.objects.filter(galaxy=galaktyka_id, system=system_id, field=planeta_id,
                                planet__owner__isnull=True).count()
    if Galaxy.objects.filter(galaxy=galaktyka_id, system=system_id, field=planeta_id,
                             planet__owner__isnull=True).count() > 0:
        message = "Niestety planeta " + str(galaktyka_id) + ":" + str(system_id) + ":" + str(
            planeta_id) + " nie istnieje"
        send_error_message(user=user, message=message)
        return False
    return True


def check_mamy_kolonizator(user, planeta):
    s_kolonizacyjne = Flota.objects.filter(kolonizacja__gt=0, lata__gt=0)
    ilosc = planeta.flota_p_set.filter(budynek__in=s_kolonizacyjne, ilosc__gt=0).count()
    if ilosc > 0:
        return True
    else:
        message = "Niestety nie posiadasz statku kolonizacyjnego"
        send_error_message(user=user, message=message)
        return False


def check_mamy_recycler(user, planeta):
    s_recyclery = Flota.objects.filter(recycler__gt=0, lata__gt=0)
    ilosc = planeta.flota_p_set.filter(budynek__in=s_recyclery, ilosc__gt=0).count()
    if ilosc > 0:
        return True
    else:
        message = "Niestety nie posiadasz statku recyclerskiego"
        send_error_message(user=user, message=message)
        return False


def is_planet_owner(user, planeta_dane, odwrotne=False):
    galaxy = Galaxy.objects.get(galaxy=planeta_dane.galaktyka_id, system=planeta_dane.system_id,
                                field=planeta_dane.planeta_id)
    planet_obj = galaxy.planet
    if not odwrotne:
        if not planet_obj.owner_id == user.pk:
            message = "Niestety planeta %s:%s:%s nie jest twoja" % (
            planeta_dane.galaktyka_id, planeta_dane.system_id, planeta_dane.planeta_id)
            send_error_message(user=user, message=message)
            return False
        return True
    else:
        if planet_obj.owner_id == user.pk:
            message = "Niestety planeta %s:%s:%s jest twoja" % (
            planeta_dane.galaktyka_id, planeta_dane.system_id, planeta_dane.planeta_id)
            send_error_message(user=user, message=message)
            return True
        return False


def get_zuzycie_deuteru(dane, planeta_dane):
    spd = 35000.0 / (dane.czas_lotu * float(FLEET_SPEED) - 10.0) * sqrt(dane.odleglosc * 10.0 / dane.speed)
    zuzycie_deuter = int(
        (dane.basic_consumption / 8) * (dane.odleglosc / 35000.0) * ((spd / 10.0) + 1) * ((spd / 10.0) + 1.0))
    return zuzycie_deuter * (planeta_dane.speed_procent / 10) + 2


def get_ship_request(GraObject, planeta, request, user, planeta_dane, check_kolonizacja=None, check_recycler=None,
                     wiadomosci=True):
    kolonizacyjny = False
    recyclerski = False
    bledne_ilosci = False
    jakikolwiek_statek = False
    dane_floty = Output()
    dane_floty.speed = False
    dane_floty.bak_pojemnosc = 0
    dane_floty.ladownosc = 0
    dane_floty.basic_consumption = 0
    id_statkow = []
    statki_podsumowanie = []
    ship_request = {}
    wszystkie_statki = Flota_p.objects.values_list("budynek_id", flat=True).select_for_update().filter(planeta=planeta,
                                                                                                       budynek__lata__gt=0,
                                                                                                       ilosc__gt=0).order_by(
        "budynek")
    for tmp in wszystkie_statki:
        i = GraObject.cache_obj.get_flota_p(planeta.pk, tmp)
        if request.REQUEST.has_key('ship_' + str(i.pk)):
            try:
                ilosc = int(request.REQUEST['ship_' + str(i.pk)])
            except:
                ilosc = 0
            if ilosc <= i.ilosc and ilosc > 0:
                ship_request[i.budynek_id] = ilosc
                id_statkow.append(i.budynek_id)
                true_speed = int(get_speed(GraObject, i.budynek, user))
                statki_podsumowanie.append({"statek": i.budynek, "ilosc": ilosc, "speed": true_speed})
                jakikolwiek_statek = True
                if not dane_floty.speed or dane_floty.speed > true_speed:
                    dane_floty.speed = true_speed
                if check_kolonizacja and i.budynek.kolonizacja > 0:
                    kolonizacyjny = True
                if check_recycler and i.budynek.recycler > 0:
                    recyclerski = True

            elif ilosc > i.ilosc:
                bledne_ilosci = True

            dane_floty.bak_pojemnosc += i.budynek.bak * ilosc
            dane_floty.basic_consumption += i.budynek.c_consumption * ilosc
            if check_recycler:
                if i.budynek.recycler:
                    dane_floty.ladownosc += i.budynek.capacity * ilosc
            else:
                dane_floty.ladownosc += i.budynek.capacity * ilosc

    # dane_floty.speed=int(dane_floty.speed*(planeta_dane.speed_procent/10))

    request.session['ship_request'] = ship_request
    request.session['id_statkow'] = id_statkow

    if bledne_ilosci:
        message = "Niestety wprowadziłeś błędne ilości statków"
        send_error_message(user=user, message=message)
        return False

    if check_kolonizacja and not kolonizacyjny:
        message = "Musisz wybrać statek kolonizacyjny"
        send_error_message(user=user, message=message)
        return False

    if check_recycler and not recyclerski:
        message = "Musisz wybrać statek recyclerski"
        send_error_message(user=user, message=message)
        return False
    if not jakikolwiek_statek:
        if wiadomosci:
            message = "Musisz wybrać statki"
            send_error_message(user=user, message=message)
        return False
    return {"id_statkow": id_statkow, "ship_request": ship_request, "dane_floty": dane_floty,
            "statki_podsumowanie": statki_podsumowanie}


def check_ship_request(GraObject, request, planeta, planeta_dane, id_statkow, ship_request, user,
                       check_kolonizacja=None, check_recycler=None):
    kolonizacyjny = False
    recyclerski = False
    bledne_ilosci = False
    jakikolwiek_statek = False
    dane_floty = Output()
    dane_floty.speed = False
    dane_floty.bak_pojemnosc = 0
    dane_floty.ladownosc = 0
    dane_floty.basic_consumption = 0
    statki_podsumowanie = []
    statki_do_wyslania = Flota_p.objects.values_list("budynek_id", flat=True).filter(planeta=planeta,
                                                                                     budynek__lata__gt=0,
                                                                                     budynek__in=id_statkow).order_by(
        "budynek")
    id_statkow = []
    for tmp in statki_do_wyslania:
        i = GraObject.cache_obj.get_flota_p(planeta.pk, tmp)
        try:
            ilosc = int(ship_request[i.budynek_id])
        except:
            ilosc = 0
        if ilosc <= i.ilosc and ilosc > 0:
            id_statkow.append(i.budynek_id)
            true_speed = int(get_speed(GraObject, i.budynek, user))
            jakikolwiek_statek = True
            statki_podsumowanie.append({"statek": i.budynek, "ilosc": ilosc, "speed": true_speed})
            if not dane_floty.speed or dane_floty.speed > true_speed:
                dane_floty.speed = true_speed
            if check_kolonizacja and i.budynek.kolonizacja > 0:
                kolonizacyjny = True
            if check_recycler and i.budynek.recycler > 0:
                recyclerski = True

        elif ilosc > i.ilosc:
            bledne_ilosci = True

        dane_floty.bak_pojemnosc += i.budynek.bak * ilosc
        if check_recycler:
            if i.budynek.recycler:
                dane_floty.ladownosc += i.budynek.capacity * ilosc
        else:
            dane_floty.ladownosc += i.budynek.capacity * ilosc
        dane_floty.basic_consumption += i.budynek.c_consumption * ilosc

    # dane_floty.speed=int(dane_floty.speed*(planeta_dane.speed_procent/10))
    request.session['id_statkow'] = id_statkow

    if bledne_ilosci:
        message = "Niestety wprowadziłeś błędne ilości statków"
        send_error_message(user=user, message=message)
        del request.session['id_statkow']
        del request.session['ship_request']
        del request.session['planeta_dane']
        return False

    if check_kolonizacja and not kolonizacyjny:
        message = "Musisz wybrać statek kolonizacyjny"
        send_error_message(user=user, message=message)
        del request.session['id_statkow']
        del request.session['ship_request']
        del request.session['planeta_dane']
        return False

    if check_recycler and not recyclerski:
        message = "Musisz wybrać statek recyclerski"
        send_error_message(user=user, message=message)
        del request.session['id_statkow']
        del request.session['ship_request']
        del request.session['planeta_dane']
        return False
    if not jakikolwiek_statek:
        message = "Musisz wybrać statki"
        send_error_message(user=user, message=message)
        return False
    return {"id_statkow": id_statkow, "ship_request": ship_request, "dane_floty": dane_floty,
            "statki_podsumowanie": statki_podsumowanie}


def wieksze_od_zera(val):
    if val > 0:
        return val
    return 0


def check_surowce(request, planeta, dane_floty):
    user = request.user
    surowce_poprawne = True
    try:
        zab_met = wieksze_od_zera(int(request.REQUEST['zab_met']))
        if zab_met > planeta.metal:
            message = "Nie masz tyle metalu na planecie"
            send_error_message(user=user, message=message)
            surowce_poprawne = False
    except:
        zab_met = 0
    try:
        zab_cry = wieksze_od_zera(int(request.REQUEST['zab_cry']))
        if zab_cry > planeta.crystal:
            message = "Nie masz tyle kryształu na planecie"
            send_error_message(user=user, message=message)
            surowce_poprawne = False
    except:
        zab_cry = 0
    try:
        zab_deu = wieksze_od_zera(int(request.REQUEST['zab_deu']))
        if zab_deu > planeta.deuter - dane_floty.zuzycie_deuter:
            message = "Nie masz tyle deuteru na planecie"
            send_error_message(user=user, message=message)
            surowce_poprawne = False
    except:
        zab_deu = 0

    zabieramy = zab_cry + zab_deu + zab_met
    if zabieramy > dane_floty.ladownosc:
        message = "Nie możesz zabrać tyle ładunku na statki"
        send_error_message(user=user, message=message)
        surowce_poprawne = False
    if not surowce_poprawne:
        return False
    return [zab_met, zab_cry, zab_deu]


def get_flota(GraObject, short=None):
    current_planet = GraObject.get_current_planet()
    spy_tech = GraObject.cache_obj.get_badanie_p(GraObject.user.pk, Badania.objects.get(szpieg=1).pk)

    if spy_tech:
        spy_tech_level = spy_tech.level
    else:
        spy_tech_level = 0
    fl_own = Fleets.objects.filter(fleet_owner=GraObject.user).order_by("time")

    galaktyki_usera = Galaxy.objects.filter(planet__in=GraObject.get_all_planets())
    fl_obce = Fleets.objects.exclude(fleet_owner=GraObject.user).filter(galaxy_end__in=galaktyki_usera).order_by("time")

    if short:
        fl_obce = fl_obce.count()
        fl_own = fl_own.count()
        return fl_own, fl_obce, fl_own + fl_obce

    floty_own = []
    floty_obce = []
    for f in fl_own:

        flota_tmp = Output()
        flota_tmp = f

        if not f.fleet_back > 0:
            flota_tmp.zawroc = 1

        flota_tmp.start_time = strftime("%d.%m.%y %H:%M:%S", localtime(f.time_start))
        flota_tmp.end_time = strftime("%d.%m.%y %H:%M:%S", localtime(f.time))
        roznica = f.time - f.time_start
        flota_tmp.back_time = strftime("%d.%m.%y %H:%M:%S", localtime(f.time + roznica))
        flota_tmp.czas_do = int(ceil(f.time - time()))

        statki = split(f.fleet_array, ";")
        flota_tmp.statki = []
        for s in statki:
            tmp = split(s, ",")
            statek = Output()
            statek.nazwa = Flota.objects.get(pk=tmp[0]).nazwa
            statek.ilosc = tmp[1]
            flota_tmp.statki.append(statek)
        if f.fleet_mission == 1:
            flota_tmp.typ_lotu = 'Kolonizuj'
        elif f.fleet_mission == 2:
            flota_tmp.typ_lotu = 'Transportuj'
        elif f.fleet_mission == 3:
            flota_tmp.typ_lotu = 'Przeslij'
        elif f.fleet_mission == 4:
            flota_tmp.typ_lotu = 'Atak'
        elif f.fleet_mission == 5:
            flota_tmp.typ_lotu = 'Złom'
        elif f.fleet_mission == 6:
            flota_tmp.typ_lotu = 'Szpieguj'
        floty_own.append(flota_tmp)

    for f in fl_obce:

        flota_tmp = Output()
        flota_tmp = f
        flota_tmp.zawroc = 0
        flota_tmp.ilosc_danych = None
        if spy_tech_level >= 15:
            flota_tmp.ilosc_danych = 'wszystkie'
        elif spy_tech_level >= 12:
            flota_tmp.ilosc_danych = 'czesciowe'

        flota_tmp.start_time = strftime("%d.%m.%y %H:%M:%S", localtime(f.time_start))
        flota_tmp.end_time = strftime("%d.%m.%y %H:%M:%S", localtime(f.time))
        roznica = f.time - f.time_start
        flota_tmp.back_time = strftime("%d.%m.%y %H:%M:%S", localtime(f.time + roznica))
        flota_tmp.czas_do = int(ceil(f.time - time()))

        if flota_tmp.ilosc_danych:
            statki = split(f.fleet_array, ";")
            flota_tmp.statki = []
            for s in statki:
                tmp = split(s, ",")
                statek = Output()
                statek.nazwa = Flota.objects.get(pk=tmp[0]).nazwa
                statek.ilosc = tmp[1]
                flota_tmp.statki.append(statek)

        if f.fleet_mission == 1:
            flota_tmp.typ_lotu = 'Kolonizuj'
        elif f.fleet_mission == 2:
            flota_tmp.typ_lotu = 'Transportuj'
        elif f.fleet_mission == 3:
            flota_tmp.typ_lotu = 'Przeslij'
        elif f.fleet_mission == 4:
            flota_tmp.typ_lotu = 'Atak'
        elif f.fleet_mission == 5:
            flota_tmp.typ_lotu = 'Złom'
        floty_obce.append(flota_tmp)
    if floty_obce or floty_own:
        floty = 1
    else:
        floty = None
    return floty_own, floty_obce, floty

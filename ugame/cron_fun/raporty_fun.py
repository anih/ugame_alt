# -*- coding: utf-8 -*-
from __future__ import division
import datetime

from django.template.loader import render_to_string

from ugame.models.all import Raporty

from random import randint


def rap_spy(dane_raport, flota):
    agresor = dane_raport['agresor']
    obronca = dane_raport['obronca']
    agresor.userprofile.nowe_raporty += 1
    obronca.userprofile.nowe_raporty += 1
    tekst_agresor = render_to_string("game/raporty/spy_agresor.html", dane_raport)
    tekst_obronca = render_to_string("game/raporty/spy_obronca.html", dane_raport)

    koordy_z = '%s:%s:%s' % (flota.galaxy_start.galaxy, flota.galaxy_start.system, flota.galaxy_start.field)
    koordy_do = '%s:%s:%s' % (flota.galaxy_end.galaxy, flota.galaxy_end.system, flota.galaxy_end.field)
    data = datetime.datetime.fromtimestamp(flota.time)

    Raporty.objects.create(typ='S', user=agresor.user, tytul="Szpiegowanie planety", tekst=tekst_agresor,
                      koordy_z=koordy_z, koordy_do=koordy_do, data=data)

    Raporty.objects.create(typ='S', user=obronca.user, tytul="Ktoś szpiegował planete", tekst=tekst_obronca,
                      koordy_z=koordy_z, koordy_do=koordy_do, data=data,)



def rap_zlom(flota, GraObj):
    GraObj.userprofile.nowe_raporty += 1
    dane_raport = {"galaxy":flota.galaxy_start, "flota":flota}
    koordy_z = '%s:%s:%s' % (flota.galaxy_start.galaxy, flota.galaxy_start.system, flota.galaxy_start.field)
    koordy_do = '%s:%s:%s' % (flota.galaxy_end.galaxy, flota.galaxy_end.system, flota.galaxy_end.field)
    data = datetime.datetime.fromtimestamp(flota.time)

    tekst = render_to_string("game/raporty/zlom.html", dane_raport)
    Raporty.objects.create(typ='Z', user=GraObj.user, tytul="Złom", tekst=tekst,
                  koordy_z=koordy_z, koordy_do=koordy_do, data=data)



def rap_surowce(flota, GraObj):
    GraObj.userprofile.nowe_raporty += 1
    dane_raport = {"galaxy":flota.galaxy_start, "flota":flota}
    koordy_z = '%s:%s:%s' % (flota.galaxy_start.galaxy, flota.galaxy_start.system, flota.galaxy_start.field)
    koordy_do = '%s:%s:%s' % (flota.galaxy_end.galaxy, flota.galaxy_end.system, flota.galaxy_end.field)
    data = datetime.datetime.fromtimestamp(flota.time)

    tekst = render_to_string("game/raporty/surowce.html", dane_raport)
    Raporty.objects.create(typ='T', user=GraObj.user, tytul="Surowce dotarły", tekst=tekst,
                  koordy_z=koordy_z, koordy_do=koordy_do, data=data)


def rap_przeslij(flota, statki_powrot, GraObj):
    GraObj.userprofile.nowe_raporty += 1
    dane_raport = {"galaxy":flota.galaxy_end, "flota":flota, "statki_powrot":statki_powrot}
    koordy_z = '%s:%s:%s' % (flota.galaxy_start.galaxy, flota.galaxy_start.system, flota.galaxy_start.field)
    koordy_do = '%s:%s:%s' % (flota.galaxy_end.galaxy, flota.galaxy_end.system, flota.galaxy_end.field)
    data = datetime.datetime.fromtimestamp(flota.time)
    tekst = render_to_string("game/raporty/przeslij.html", dane_raport)

    rap = Raporty.objects.create(typ='P', user=GraObj.user, tytul="Flota z misja prześlij dla planety " + koordy_do, tekst=tekst,
                  koordy_z=koordy_z, koordy_do=koordy_do, data=data)


def rap_powrot(flota, statki_powrot, GraObj):
    GraObj.userprofile.nowe_raporty += 1
    dane_raport = {"galaxy":flota.galaxy_start, "flota":flota, "statki_powrot":statki_powrot}
    koordy_z = '%s:%s:%s' % (flota.galaxy_start.galaxy, flota.galaxy_start.system, flota.galaxy_start.field)
    koordy_do = '%s:%s:%s' % (flota.galaxy_end.galaxy, flota.galaxy_end.system, flota.galaxy_end.field)
    data = datetime.datetime.fromtimestamp(flota.time)

    tekst = render_to_string("game/raporty/powrot.html", dane_raport)
    Raporty.objects.create(typ='B', user=GraObj.user, tytul="Powrót z galaktyki", tekst=tekst,
                  koordy_z=koordy_z, koordy_do=koordy_do, data=data)

def rap_atak(dane_raport, flota, wygrana):
    '''
    dane_raport = {"agresor":agresor,"obronca":obronca,"rundy":rundy,"surowce_zdobyte":surowce_zdobyte,
                                              "galaktyka":obronca_galaktyka,"obronca_obrona":obronca_obrona,"obronca_statki":obronca_statki,
                                              "agresor_statki":agresor_statki,"obronca_dane":obronca_dane,"agresor_dane":agresor_dane}
    '''
    agresor = dane_raport['agresor']
    agresor.userprofile.nowe_raporty += 1

    obronca = dane_raport['obronca']
    obronca.userprofile.nowe_raporty += 1

    if len(dane_raport['dane'].rundy) > 1 or wygrana != 'O':
        agresor_spy = dane_raport['agresor_dane'].spy_tech
        obronca_spy = dane_raport['obronca_dane'].spy_tech
        if agresor_spy < obronca_spy:
            dane_raport['bez_technologii'] = 1
        elif agresor_spy == obronca_spy:
            if randint(1, 5) == 3:
                dane_raport['bez_technologii'] = 1
        tekst_agresor = render_to_string("game/raporty/atak.html", dane_raport)
        # print tekst_agresor
    else:
        tekst_agresor = render_to_string("game/raporty/atak_przerwany.html")

    koordy_z = '%s:%s:%s' % (flota.galaxy_start.galaxy, flota.galaxy_start.system, flota.galaxy_start.field)
    koordy_do = '%s:%s:%s' % (flota.galaxy_end.galaxy, flota.galaxy_end.system, flota.galaxy_end.field)
    data = datetime.datetime.fromtimestamp(flota.time)

    Raporty.objects.create(typ='A', user=agresor.user, tytul="Atak na planetę", tekst=tekst_agresor,
                      koordy_z=koordy_z, koordy_do=koordy_do, data=data)

    dane_raport['bez_technologii'] = None
    tekst_obronca = render_to_string("game/raporty/atak.html", dane_raport)
    Raporty.objects.create(typ='A', user=obronca.user, tytul="Obrona planety", tekst=tekst_obronca,
                      koordy_z=koordy_z, koordy_do=koordy_do, data=data,)


def kolonizajca_fail_planety(flota, GraObj):
    GraObj.userprofile.nowe_raporty += 1
    dane_raport = {"galaxy":flota.galaxy_end, "flota":flota}
    tekst = render_to_string("game/raporty/kolonizacja_fail.html", dane_raport)
    koordy_z = '%s:%s:%s' % (flota.galaxy_start.galaxy, flota.galaxy_start.system, flota.galaxy_start.field)
    koordy_do = '%s:%s:%s' % (flota.galaxy_end.galaxy, flota.galaxy_end.system, flota.galaxy_end.field)
    data = datetime.datetime.fromtimestamp(flota.time)
    Raporty.objects.create(typ='K',
                      user=flota.fleet_owner, tytul="Kolonizacja nie powiodła się",
                      tekst=tekst,
                      koordy_z=koordy_z, koordy_do=koordy_do, data=data)


def kolonizacja_fail_ktoinny(flota, GraObj):
    GraObj.userprofile.nowe_raporty += 1
    dane_raport = {"galaxy":flota.galaxy_end, "flota":flota}
    tekst = render_to_string("game/raporty/kolonizacja_fail_ktoinny.html", dane_raport)
    koordy_z = '%s:%s:%s' % (flota.galaxy_start.galaxy, flota.galaxy_start.system, flota.galaxy_start.field)
    koordy_do = '%s:%s:%s' % (flota.galaxy_end.galaxy, flota.galaxy_end.system, flota.galaxy_end.field)
    data = datetime.datetime.fromtimestamp(flota.time)
    Raporty.objects.create(typ='K', user=flota.fleet_owner, tytul="Kolonizacja nie powiodła się", tekst=tekst,
                        koordy_z=koordy_z, koordy_do=koordy_do, data=data)

def kolonizacja_ok(flota, GraObj):
    GraObj.userprofile.nowe_raporty += 1
    dane_raport = {"galaxy":flota.galaxy_end, "flota":flota}
    tekst = render_to_string("game/raporty/kolonizacja_ok.html", dane_raport)
    koordy_z = '%s:%s:%s' % (flota.galaxy_start.galaxy, flota.galaxy_start.system, flota.galaxy_start.field)
    koordy_do = '%s:%s:%s' % (flota.galaxy_end.galaxy, flota.galaxy_end.system, flota.galaxy_end.field)
    data = datetime.datetime.fromtimestamp(flota.time)
    Raporty.objects.create(typ='K', user=flota.fleet_owner, tytul="Kolonizacja", tekst=tekst,
                      koordy_z=koordy_z, koordy_do=koordy_do, data=data)

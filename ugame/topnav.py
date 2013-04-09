from __future__ import division
from django.shortcuts import get_object_or_404
from main.models import Config
from ugame.models import Planets
from ugame.models import Lang
from ugame.models import Galaxy
from ugame.models import Fleets
from django.contrib.auth.models import User
from math import floor
from time import localtime
import datetime

class Output:pass


def topnav_site(GraObject):
    current_planet = GraObject.get_current_planet()
    topnav = Output()
    if GraObject.userprofile.new_message > 0:
        topnav.new_message = GraObject.userprofile.new_message

    if GraObject.userprofile.nowe_raporty > 0:
        topnav.nowe_raporty = GraObject.userprofile.nowe_raporty
    # TODO funkcja aktualizujaca planete
    topnav.image = current_planet.image
    topnav.plist = []

    zaznaczona = False
    topnav.prevp = None
    topnav.nextp = None
    for pl  in GraObject.get_all_planets():
        pl = GraObject.get_planet(pl)
        if pl.destroyed == 0:
            planet = Output()
            planet.pl = pl

            if pl.id == current_planet.pk:
                planet.selected = 1
                pozycja = len(topnav.plist) - 1
                if pozycja >= 0:
                    topnav.prevp = topnav.plist[len(topnav.plist) - 1].pl
                zaznaczona = True
            else:
                if zaznaczona == True:
                    zaznaczona = False
                    topnav.nextp = pl
            topnav.plist.append(planet)

    topnav.energy = floor(current_planet.energy_max - current_planet.energy_used)

    if topnav.energy > 0:topnav.energy_color = '#00FF00'
    else:topnav.energy_color = '#FF0000'

    if current_planet.metal < current_planet.metal_max:topnav.metal_color = '#00FF00'
    else:topnav.metal_color = '#FF0000'

    if current_planet.crystal < current_planet.crystal_max:topnav.crystal_color = '#00FF00'
    else:topnav.crystal_color = '#FF0000'

    if current_planet.deuter < current_planet.deuter_max:topnav.deuter_color = '#00FF00'
    else:topnav.deuter_color = '#FF0000'
    gm = localtime()
    topnav.czas_serwera = gm[3] * 3600 + gm[4] * 60 + gm[5]
    czas_od_klikniecia = datetime.datetime.now() - datetime.timedelta(minutes=10)
    topnav.users_online = User.objects.filter(last_login__gte=czas_od_klikniecia).count()
    topnav.cp = current_planet
    return topnav

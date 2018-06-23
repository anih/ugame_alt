# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User

from ugame.models.all import Planets
from ugame.models.all import UserProfile

from ..klasy.BaseHelper import BaseHelper
from ..klasy.BuildBuilding import BuildBuilding
from ..klasy.BuildFleet import BuildFleet
from ..klasy.BuildObrona import BuildObrona
from ..klasy.BuildTech import BuildTech
from ..klasy.CacheClass import CacheClass
from ..klasy.CronBase import CronBase
from ..klasy.SojuszHelper import SojuszHelper


class Output(): pass


class BaseGame(BaseHelper, CronBase, BuildBuilding, BuildFleet, BuildObrona, BuildTech, SojuszHelper):
    view = None
    request = None
    user = None
    userprofile = None
    cache_obj = None
    czy_zapis = False

    def __init__(self, view, czas_teraz=None, cron=True):
        self.view = view
        self.request = getattr(view, 'request', None)
        self.user = None
        self.userprofile = None
        self.current_planet_id = None
        self.user_planets = {}
        self.galaktyki = {}
        self.cache_budynki_p = {}
        self.cache_obj = CacheClass()
        self.czy_zapis = False
        self.sojusz_usera = None
        self.sojusz_czlonek = None

        self.lock_user()

        if cron:
            self.cron_function(self.current_planet_id, czas_teraz)

    def save_all(self):
        self.czy_zapis = True
        self.user.save(force_update=True)
        self.userprofile.save(force_update=True)

        for p in self.user_planets:
            self.user_planets[p].save(force_update=True)
        for p in self.galaktyki:
            self.galaktyki[p].save(force_update=True)
        self.cache_obj.save_all()
        # from django.db.transaction import rollback
        # rollback()

    def send_message(self, message):
        messages.info(self.request, message=message)
        return True

    def userprofile_podglad_flota(self):
        if "userprofile_podglad_flota" in self.request.REQUEST:
            if self.userprofile.podglad_flota:
                self.userprofile.podglad_flota = False
            else:
                self.userprofile.podglad_flota = True

    def lock_user(self):
        self.user = User.objects.select_for_update().get(pk=self.view.user.id)
        self.userprofile = UserProfile.objects.select_for_update().get(user=self.user)
        if self.request:
            self.user.last_login = datetime.now()

        self.change_planet()
        if Planets.objects.filter(pk=self.userprofile.current_planet_id).count() > 0:
            self.current_planet_id = self.userprofile.current_planet_id
        else:
            self.userprofile.current_planet = Planets.objects.select_for_update().filter(owner=self.user)[0]
            self.current_planet_id = self.userprofile.current_planet_id

    def lock_alien_user(self, user_id):
        user = User.objects.select_for_update().get(pk=user_id)
        userprofile = UserProfile.objects.select_for_update().get(user=user)
        return user, userprofile

    def change_planet(self):
        if not self.request:
            return
        if "cp" in self.request.GET:
            if int(self.request.GET['cp']) > 0:
                if self.user.planets_set.filter(pk=self.request.GET['cp']).count() > 0:

                    planeta_nowa = self.get_planet(self.request.GET['cp'])
                    self.userprofile.current_planet = planeta_nowa

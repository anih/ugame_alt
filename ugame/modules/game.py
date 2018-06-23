# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from time import strftime

from django.contrib.auth.models import User
from django.db import connection

import ugame.funkcje as fun
from ugame.models.all import UserProfile
from ugame.topnav import topnav_site

from ..generic.cms_metaclass import CmsMetaclass


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        self.game.userprofile_podglad_flota()
        if "fs_zawroc" in self.request.REQUEST:
            fun.zawroc(self.request.REQUEST['fs_zawroc'], self.game.user)

        if "rename_planet" in self.request.REQUEST:
            self.game.rename_planet(self.request.REQUEST["rename_planet"])

        current_planet = self.game.get_current_planet()

        galaxyrow = self.game.get_galaxy(current_planet.galaxy_id)
        planety_klucze = self.game.get_all_planets()
        planety_klucze.remove(self.game.current_planet_id)

        output = fun.Output()
        output.planets = []

        for k in planety_klucze:
            output.planets.append(self.game.get_planet(k))

        output.other_data = fun.Output()
        output.other_data.time = strftime("%c")  # strftime("%a %b %H:%M:%S")#date("D M d H:i:s",time());

        output.current_planet = current_planet

        if (galaxyrow):
            output.current_galaxy = galaxyrow

        output.user_data = fun.Output()
        output.user_data.user_rank = UserProfile.objects.filter(points__gt=self.game.userprofile.points).order_by(
            "-points").count() + 1
        output.user_data.userprofile = self.game.userprofile
        output.user_data.user = self.game.user
        output.user_data.user_points = int(self.game.userprofile.points_obrona) + int(
            self.game.userprofile.points_builds) + int(self.game.userprofile.points_flota) + int(
            self.game.userprofile.points_tech)

        output.other_data.max_users = User.objects.all().count()

        output.current_zajete = fun.Output()
        output.current_zajete.budowanie = current_planet.zajety_budowaniem()
        output.current_zajete.badanie = current_planet.zajety_badaniem()
        output.current_zajete.obrona = current_planet.zajety_obrona()
        output.current_zajete.flota = current_planet.zajety_flota()

        if not output.current_zajete.budowanie and not output.current_zajete.badanie and not output.current_zajete.obrona and not output.current_zajete.flota:
            output.current_zajete.building_free = "Oczekuje"

        topnav = topnav_site(self.game)

        timesql = 0.0
        for q in connection.queries:
            if 'time' in q:
                timesql += float(q['time'])
        seen = {}
        duplicate = 0
        for q in connection.queries:
            sql = q["sql"]
            c = seen.get(sql, 0)
            if c:
                duplicate += 1
            q["seen"] = c
            seen[sql] = c + 1

        if self.game.userprofile.podglad_flota == True:
            floty_own, floty_obce, floty = fun.get_flota(self.game)
        else:
            floty_own, floty_obce, floty = fun.get_flota(self.game, 1)

        output.other_data.procent = current_planet.get_procent_producji()

        return {
            'output': output, 'topnav': topnav,
            "floty": floty, "floty_own": floty_own,
            "floty_obce": floty_obce, "sqltime": timesql,
            "duplicate": duplicate,
        }

    site_main.url = "^ugame/$"

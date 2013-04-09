# -*- coding: utf-8 -*-
from ..generic.cms_metaclass import CmsMetaclass
from ugame.klasy.BaseGame import BaseGame
from ugame.topnav import topnav_site
import ugame.funkcje as fun
from math import ceil
from time import strftime
from ugame.models.all import UserProfile
from django.contrib.auth.models import User
from django.db import connection
from settings import STATS_PERPAGE


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self):
        GraObject = BaseGame(self)
        GraObject.userprofile_podglad_flota()
        if "fs_zawroc" in self.request.REQUEST:
            fun.zawroc(self.request.REQUEST['fs_zawroc'], GraObject.user)

        if "rename_planet" in self.request.REQUEST:
            GraObject.rename_planet(self.request.REQUEST["rename_planet"])

        current_planet = GraObject.get_current_planet()

        galaxyrow = GraObject.get_galaxy(current_planet.galaxy_id)
        planety_klucze = GraObject.get_all_planets()
        planety_klucze.remove(GraObject.current_planet_id)

        output = fun.Output()
        output.planets = []

        for k in planety_klucze:
            output.planets.append(GraObject.get_planet(k))

        output.other_data = fun.Output()
        output.other_data.time = strftime("%c")  # strftime("%a %b %H:%M:%S")#date("D M d H:i:s",time());

        output.current_planet = current_planet

        if(galaxyrow):
            output.current_galaxy = galaxyrow

        output.user_data = fun.Output()
        output.user_data.user_rank = UserProfile.objects.filter(points__gt=GraObject.userprofile.points).order_by("-points").count() + 1
        output.user_data.userprofile = GraObject.userprofile
        output.user_data.user = GraObject.user
        output.user_data.user_points = int(GraObject.userprofile.points_obrona) + int(GraObject.userprofile.points_builds) + int(GraObject.userprofile.points_flota) + int(GraObject.userprofile.points_tech)

        output.other_data.max_users = User.objects.all().count()

        output.current_zajete = fun.Output()
        output.current_zajete.budowanie = current_planet.zajety_budowaniem()
        output.current_zajete.badanie = current_planet.zajety_badaniem()
        output.current_zajete.obrona = current_planet.zajety_obrona()
        output.current_zajete.flota = current_planet.zajety_flota()

        if not output.current_zajete.budowanie and not output.current_zajete.badanie and not output.current_zajete.obrona and not output.current_zajete.flota:
            output.current_zajete.building_free = "Oczekuje"

        topnav = topnav_site(GraObject)

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

        if GraObject.userprofile.podglad_flota == True:
            floty_own, floty_obce, floty = fun.get_flota(GraObject)
        else:
            floty_own, floty_obce, floty = fun.get_flota(GraObject, 1)

        output.other_data.procent = current_planet.get_procent_producji()

        stats_page = int(ceil(float(UserProfile.objects.filter(points__gt=self.user.userprofile.points).count()) / STATS_PERPAGE))

        return {
                'output': output, 'topnav': topnav,
                "floty": floty, "floty_own": floty_own,
                "floty_obce": floty_obce, "sqltime": timesql,
                "duplicate": duplicate, "stats_page": stats_page,
                }
    site_main.url = "^ugame/$"

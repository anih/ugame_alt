# -*- coding: utf-8 -*-
from ..generic.cms_metaclass import CmsMetaclass
from ugame.topnav import topnav_site, Output
from settings import MAX_GALAXY, MAX_SYSTEM, MAX_PLANETA
from ugame.models.all import Galaxy
from ugame import models


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self, galaxy=None, system=None):
        current_planet = self.game.get_current_planet()
        print current_planet.pk
        current_galaxy = self.game.get_galaxy(current_planet.galaxy_id)
        print current_galaxy.planet.pk

        try:
            galaxy = int(galaxy)
        except:
            pass
        try:
            system = int(system)
        except:
            pass

        try:
            galaxy = int(self.request.REQUEST['galaxy'])
        except:
            pass
        try:
            system = int(self.request.REQUEST['system'])
        except:
            pass

        if not galaxy > 0 or galaxy > MAX_GALAXY:
            galaxy = current_galaxy.galaxy
        if not system > 0 or system > MAX_SYSTEM:
            system = current_galaxy.system
        if galaxy > MAX_GALAXY:
            galaxy = 1
        if system > MAX_SYSTEM:
            system = 1

        fields = []
        dane = Output()
        dane.galaxy = galaxy
        dane.system = system
        for i in range(1, MAX_PLANETA + 1):
            try:
                fields.append(Galaxy.objects.get(galaxy=galaxy, system=system, field=i))
            except:
                fields.append(None)

        topnav = topnav_site(self.game)
        jsbody = 'onmousemove="tt_Mousemove(event);"'
        return {
                "jsbody": jsbody, "topnav": topnav,
                "fields": fields, "dane": dane, "models": models,
                }

    site_main.url = "^ugame/galaxy/$"

# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from settings import MAX_GALAXY
from settings import MAX_PLANETA
from settings import MAX_SYSTEM
from ugame import models
from ugame.models.all import Galaxy
from ugame.topnav import Output
from ugame.topnav import topnav_site

from ..generic.cms_metaclass import CmsMetaclass


class CMS(object):
    """
    @DynamicAttrs
    """

    __metaclass__ = CmsMetaclass

    def site_main(self, galaxy=None, system=None):
        current_planet = self.game.get_current_planet()
        current_galaxy = self.game.get_galaxy(current_planet.galaxy_id)

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

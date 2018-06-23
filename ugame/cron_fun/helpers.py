# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def make_fleet_back(fl):
    galaxy_end = fl.galaxy_end
    fl.galaxy_end = fl.galaxy_start
    fl.galaxy_start = galaxy_end
    czas_lotu = fl.time - fl.time_start
    fl.time_start += czas_lotu
    fl.time += czas_lotu
    fl.fleet_back = 1
    fl.bak = 0
    fl.save(force_update=True)

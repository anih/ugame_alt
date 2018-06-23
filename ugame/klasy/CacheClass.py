# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ugame.models.all import Badania_f
from ugame.models.all import Badania_p
from ugame.models.all import Budynki_f
from ugame.models.all import Budynki_p
from ugame.models.all import Flota_f
from ugame.models.all import Flota_p
from ugame.models.all import Obrona_f
from ugame.models.all import Obrona_p


class CacheClass():
    cache_budynki_p = {}
    cache_budynki_f = {}

    cache_badania_p = {}
    cache_badania_f = {}

    cache_flota_p = {}
    cache_flota_f = {}

    cache_obrona_p = {}
    cache_obrona_f = {}

    def __init__(self):
        self.cache_budynki_p = {}
        self.cache_budynki_f = {}

        self.cache_badania_p = {}
        self.cache_badania_f = {}

        self.cache_flota_p = {}
        self.cache_flota_f = {}

        self.cache_obrona_p = {}
        self.cache_obrona_f = {}

    def save_all(self):
        for pl in self.cache_budynki_p:
            for bd in self.cache_budynki_p[pl]:
                self.cache_budynki_p[pl][bd].save(force_update=True)

        for pl in self.cache_budynki_f:
            for bd in self.cache_budynki_f[pl]:
                self.cache_budynki_f[pl][bd].save(force_update=True)

        for us in self.cache_badania_p:
            for bd in self.cache_badania_p[us]:
                self.cache_badania_p[us][bd].save(force_update=True)

        for us in self.cache_badania_f:
            for bd in self.cache_badania_f[us]:
                self.cache_badania_f[us][bd].save(force_update=True)

        for pl in self.cache_flota_p:
            for bd in self.cache_flota_p[pl]:
                self.cache_flota_p[pl][bd].save(force_update=True)

        for pl in self.cache_flota_f:
            for bd in self.cache_flota_f[pl]:
                self.cache_flota_f[pl][bd].save(force_update=True)

        for pl in self.cache_obrona_p:
            for bd in self.cache_obrona_p[pl]:
                self.cache_obrona_p[pl][bd].save(force_update=True)

        for pl in self.cache_obrona_f:
            for bd in self.cache_obrona_f[pl]:
                self.cache_obrona_f[pl][bd].save(force_update=True)

    def get_budynek_p(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)
        if not self.cache_budynki_p.has_key(id_planety):
            self.cache_budynki_p[id_planety] = {}
        if self.cache_budynki_p[id_planety].has_key(id_budynek):
            return self.cache_budynki_p[id_planety][id_budynek]
        else:
            if Budynki_p.objects.filter(planeta=id_planety, budynek=id_budynek).count() > 0:
                budynek = Budynki_p.objects.select_for_update().get(planeta=id_planety, budynek=id_budynek)
                self.cache_budynki_p[id_planety][id_budynek] = budynek
                return self.cache_budynki_p[id_planety][id_budynek]
            else:
                return None

    def del_budynek_p(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)
        self.cache_budynki_p[id_planety][id_budynek].delete()
        del self.cache_budynki_p[id_planety][id_budynek]

    def get_budynek_f(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)
        if not self.cache_budynki_f.has_key(id_planety):
            self.cache_budynki_f[id_planety] = {}
        if self.cache_budynki_f[id_planety].has_key(id_budynek):
            return self.cache_budynki_f[id_planety][id_budynek]
        else:
            if Budynki_f.objects.filter(planeta=id_planety, pk=id_budynek).count() > 0:
                budynek = Budynki_f.objects.select_for_update().get(planeta=id_planety, pk=id_budynek)
                self.cache_budynki_f[id_planety][id_budynek] = budynek
                return self.cache_budynki_f[id_planety][id_budynek]
            else:
                return None

    def del_budynek_f(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)
        self.cache_budynki_f[id_planety][id_budynek].delete()
        del self.cache_budynki_f[id_planety][id_budynek]

    def get_badanie_p(self, id_user, id_badanie):
        id_badanie = int(id_badanie)
        id_user = int(id_user)

        if not self.cache_badania_p.has_key(id_user):
            self.cache_badania_p[id_user] = {}
        if self.cache_badania_p[id_user].has_key(id_badanie):
            return self.cache_badania_p[id_user][id_badanie]
        else:
            if Badania_p.objects.filter(user=id_user, badanie=id_badanie).count() > 0:
                badanie = Badania_p.objects.select_for_update().get(user=id_user, badanie=id_badanie)
                self.cache_badania_p[id_user][id_badanie] = badanie
                return self.cache_badania_p[id_user][id_badanie]
            else:
                return None

    def del_badanie_p(self, id_user, id_badanie):
        id_badanie = int(id_badanie)
        id_user = int(id_user)

        self.cache_badania_p[id_user][id_badanie].delete()
        del self.cache_badania_p[id_user][id_badanie]

    def get_badanie_f(self, id_user, id_badanie):
        id_badanie = int(id_badanie)
        id_user = int(id_user)

        if not self.cache_badania_f.has_key(id_user):
            self.cache_badania_f[id_user] = {}
        if self.cache_badania_f[id_user].has_key(id_badanie):
            return self.cache_badania_f[id_user][id_badanie]
        else:
            if Badania_f.objects.filter(user=id_user, pk=id_badanie).count() > 0:
                badanie = Badania_f.objects.select_for_update().get(user=id_user, pk=id_badanie)
                self.cache_badania_f[id_user][id_badanie] = badanie
                return self.cache_badania_f[id_user][id_badanie]
            else:
                return None

    def del_badanie_f(self, id_user, id_badanie):
        id_badanie = int(id_badanie)
        id_user = int(id_user)

        self.cache_badania_f[id_user][id_badanie].delete()
        del self.cache_badania_f[id_user][id_badanie]

    def get_flota_p(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)

        if not self.cache_flota_p.has_key(id_planety):
            self.cache_flota_p[id_planety] = {}
        if self.cache_flota_p[id_planety].has_key(id_budynek):
            return self.cache_flota_p[id_planety][id_budynek]
        else:
            if Flota_p.objects.filter(planeta=id_planety, budynek=id_budynek).count() > 0:
                budynek = Flota_p.objects.select_for_update().get(planeta=id_planety, budynek=id_budynek)
                self.cache_flota_p[id_planety][id_budynek] = budynek
                return self.cache_flota_p[id_planety][id_budynek]
            else:
                return None

    def del_flota_p(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)

        self.cache_flota_p[id_planety][id_budynek].delete()
        del self.cache_flota_p[id_planety][id_budynek]

    def get_flota_f(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)

        if not self.cache_flota_f.has_key(id_planety):
            self.cache_flota_f[id_planety] = {}
        if self.cache_flota_f[id_planety].has_key(id_budynek):
            return self.cache_flota_f[id_planety][id_budynek]
        else:
            if Flota_f.objects.filter(planeta=id_planety, pk=id_budynek).count() > 0:
                budynek = Flota_f.objects.select_for_update().get(planeta=id_planety, pk=id_budynek)
                self.cache_flota_f[id_planety][id_budynek] = budynek
                return self.cache_flota_f[id_planety][id_budynek]
            else:
                return None

    def del_flota_f(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)

        self.cache_flota_f[id_planety][id_budynek].delete()
        del self.cache_flota_f[id_planety][id_budynek]

    def get_obrona_p(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)

        if not self.cache_obrona_p.has_key(id_planety):
            self.cache_obrona_p[id_planety] = {}
        if self.cache_obrona_p[id_planety].has_key(id_budynek):
            return self.cache_obrona_p[id_planety][id_budynek]
        else:
            if Obrona_p.objects.filter(planeta=id_planety, budynek=id_budynek).count() > 0:
                budynek = Obrona_p.objects.select_for_update().get(planeta=id_planety, budynek=id_budynek)
                self.cache_obrona_p[id_planety][id_budynek] = budynek
                return self.cache_obrona_p[id_planety][id_budynek]
            else:
                return None

    def del_obrona_p(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)

        self.cache_obrona_p[id_planety][id_budynek].delete()
        del self.cache_obrona_p[id_planety][id_budynek]

    def get_obrona_f(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)

        if not self.cache_obrona_f.has_key(id_planety):
            self.cache_obrona_f[id_planety] = {}
        if self.cache_obrona_f[id_planety].has_key(id_budynek):
            return self.cache_obrona_f[id_planety][id_budynek]
        else:
            if Obrona_f.objects.filter(planeta=id_planety, pk=id_budynek).count() > 0:
                budynek = Obrona_f.objects.select_for_update().get(planeta=id_planety, pk=id_budynek)
                self.cache_obrona_f[id_planety][id_budynek] = budynek
                return self.cache_obrona_f[id_planety][id_budynek]
            else:
                return None

    def del_obrona_f(self, id_planety, id_budynek):
        id_budynek = int(id_budynek)
        id_planety = int(id_planety)

        self.cache_obrona_f[id_planety][id_budynek].delete()
        del self.cache_obrona_f[id_planety][id_budynek]

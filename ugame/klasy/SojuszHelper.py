# -*- coding: utf-8 -*-
from __future__ import division
from time import localtime, strftime, time
from string import split
from math import sqrt

from django.contrib.auth.models import User
from ugame.models.all import Zaproszenia, Czlonkowie, Sojusz

class Output():pass

class SojuszHelper():
    sojusz_usera = None
    sojusz_czlonek = None

    def soj_czy_moze_edytowac_opis(self):
        sojusz = self.get_sojusz()
        if not sojusz:return False
        czlonek = self.get_sojusz_czlonek()
        if czlonek.wlasciciel or czlonek.zmiana_opisu:
            return True
        return False

    def soj_czy_moze_zapraszac(self):
        sojusz = self.get_sojusz()
        if not sojusz:return False
        czlonek = self.get_sojusz_czlonek()
        if czlonek.wlasciciel or czlonek.wysylanie_zaproszen:
            return True
        return False

    def soj_czy_moze_wyrzucac(self):
        sojusz = self.get_sojusz()
        if not sojusz:return False
        czlonek = self.get_sojusz_czlonek()
        if czlonek.wlasciciel or czlonek.wyrzucanie:
            return True
        return False
    def soj_czy_zalozyciel(self):
        sojusz = self.get_sojusz()
        if not sojusz:return False
        czlonek = self.get_sojusz_czlonek()
        if czlonek.wlasciciel:
            return True
        return False

    def soj_czy_nie_zaproszony(self, user, sojusz):
        test = Zaproszenia.objects.select_for_update().filter(sojusz=sojusz, user=user).count()
        if test > 0:
            return False
        return True
    def soj_czy_nie_nalezy(self, user, sojusz):
        test = Czlonkowie.objects.select_for_update().filter(user=user, sojusz=sojusz).count()
        if test > 0:
            return False
        return True

    def get_sojusz_czlonek(self):
        if not self.sojusz_czlonek:
            sojusz_czlonek = Czlonkowie.objects.select_for_update().get(user=self.user)
            self.sojusz_czlonek = sojusz_czlonek
        return self.sojusz_czlonek

    def get_sojusz(self):
        if not self.sojusz_usera:
            try:
                sojusz = Sojusz.objects.select_for_update().get(czlonkowie__user=self.user)
                self.sojusz_usera = sojusz
            except:pass
        return self.sojusz_usera

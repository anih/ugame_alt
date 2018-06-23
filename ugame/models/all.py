# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from time import time

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields import IntegerField

from ugame.models.constants import APP_LABEL

SUROWCE = (
             ("M", "Metal"),
             ("K", "Kryształ"),
             ("D", "Deuter"),
             )


class BigIntegerField(IntegerField):
    empty_strings_allowed = False

    def get_internal_type(self):
        return "BigIntegerField"

    def db_type(self):
        return 'NUMBER(19)' if settings.DATABASE_ENGINE == 'oracle' else 'bigint'

TAK_NIE = (
             ("T", "Tak"),
             ("N", "Nie"),
             )


class Smiles(models.Model):
    objects = models.Manager()
    tag = models.CharField(max_length=255)
    img = models.CharField(max_length=255)

    class Meta:
        app_label = APP_LABEL


class IPAccess(models.Model):
    objects = models.Manager()
    ip = models.IPAddressField(unique=True, db_index=True)
    ip_wewn = models.IPAddressField(null=True, blank=True)
    user = models.ForeignKey(User, verbose_name='user that authenticates')
    data = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.ip

    class Meta:
        app_label = APP_LABEL
        verbose_name = 'IP Access'
        verbose_name_plural = 'IP Accesses'

    class Admin:
        list_display = ('ip', 'user')


# Create your models here.
class Errors(models.Model):
    objects = models.Manager()
    text = models.TextField(max_length=1024)


class Raporty(models.Model):
    objects = models.Manager()
    TYP = (
         ("K", "Kolonizacja"),
         ("P", "Prześlij"),
         ("T", "Transport"),
         ("A", "Atak"),
         ("S", "Szpiegowski"),
         ("B", "Powroty"),
         )
    user = models.ForeignKey(User)
    tytul = models.CharField(max_length=255)
    tekst = models.TextField(max_length=1024)
    data = models.DateTimeField(auto_now_add=True)
    koordy_z = models.CharField(max_length=32)
    koordy_do = models.CharField(max_length=32)
    typ = models.CharField(max_length=1, choices=TYP, default='', null=True, blank=True)

    class Meta:
        app_label = APP_LABEL


class Buildings(models.Model):
    objects = models.Manager()
    nazwa = models.CharField(max_length=255)
    opis = models.TextField()
    opis_dlugi = models.TextField()
    opis_dodatkowy = models.TextField()
    c_met = models.IntegerField(max_length=11)
    c_cry = models.IntegerField(max_length=11)
    c_deu = models.IntegerField(max_length=11)
    c_ene = models.IntegerField(max_length=11)
    c_powierzchnia = models.IntegerField(max_length=11)
    c_powierzchnia_level = models.IntegerField(max_length=11)
    c_factor = models.FloatField()
    c_czas = models.IntegerField(max_length=11)
    minus_czas_tak = models.IntegerField(max_length=2)
    minus_czas = models.TextField()
    minus_czas_bad_tak = models.IntegerField(max_length=2)
    minus_czas_bad = models.TextField()
    minus_czas_flota_tak = models.IntegerField(max_length=2)
    minus_czas_flota = models.TextField()
    met = models.IntegerField(max_length=11)
    cry = models.IntegerField(max_length=11)
    deu = models.IntegerField(max_length=11)
    ene = models.IntegerField(max_length=11)
    factor = models.FloatField()
    met_formula = models.CharField(max_length=255)
    cry_formula = models.CharField(max_length=255)
    deu_formula = models.CharField(max_length=255)
    ene_formula = models.CharField(max_length=255)
    mag_met = models.IntegerField(max_length=2, default=0)
    mag_cry = models.IntegerField(max_length=2, default=0)
    mag_deu = models.IntegerField(max_length=2, default=0)
    czy_produkcja = models.IntegerField(max_length=2)
    terraformer = models.IntegerField(max_length=2)
    w_bud = models.CharField(max_length=255)
    w_bad = models.CharField(max_length=255)

    class Meta:
        app_label = APP_LABEL


class Badania(models.Model):
    objects = models.Manager()
    nazwa = models.CharField(max_length=255)
    opis = models.TextField()
    opis_dlugi = models.TextField()
    opis_dodatkowy = models.TextField()
    c_met = models.IntegerField(max_length=11)
    c_cry = models.IntegerField(max_length=11)
    c_deu = models.IntegerField(max_length=11)
    c_ene = models.IntegerField(max_length=11)
    # c_czas = models.IntegerField(max_length=11)
    c_factor = models.FloatField()
    met = models.IntegerField(max_length=11)
    cry = models.IntegerField(max_length=11)
    deu = models.IntegerField(max_length=11)
    ene = models.IntegerField(max_length=11)
    factor = models.FloatField()
    met_formula = models.CharField(max_length=255)
    cry_formula = models.CharField(max_length=255)
    deu_formula = models.CharField(max_length=255)
    ene_formula = models.CharField(max_length=255)
    szpieg = models.IntegerField(max_length=2)
    komputerowa = models.BooleanField(default=False)
    atak = models.IntegerField(max_length=2)
    ochrona = models.IntegerField(max_length=2)
    pancerz = models.IntegerField(max_length=2)
    speed_factor = models.FloatField()
    siec_badan = models.IntegerField(max_length=2)
    w_bud = models.CharField(max_length=255)
    w_bad = models.CharField(max_length=255)
    budynki_laczy_level = models.ForeignKey(Buildings)

    class Meta:
        app_label = APP_LABEL


class Galaxy(models.Model):
    objects = models.Manager()
    planet = models.ForeignKey("Planets", null=True, related_name="favoured_by")
    luna = models.ForeignKey("Lunas", null=True)
    galaxy = models.IntegerField(max_length=2, default=0)
    system = models.IntegerField(max_length=3, default=0)
    field = models.IntegerField(max_length=2, default=0)
    metal = models.IntegerField(max_length=20, default=0)
    crystal = models.IntegerField(max_length=20, default=0)
    temp_max = models.IntegerField(max_length=11, default=0)
    temp_min = models.IntegerField(max_length=11, default=0)

    class Meta:
        app_label = APP_LABEL


class Lunas(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=11)
    image = models.CharField(max_length=11)
    destroyed = models.IntegerField(max_length=3, default=0)
    user = models.ForeignKey(User)
    temp_max = models.IntegerField(max_length=11, default=0)
    temp_min = models.IntegerField(max_length=11, default=0)
    diameter = models.IntegerField(max_length=11, default=0)

    class Meta:
        app_label = APP_LABEL


class Planets(models.Model):
    objects = models.Manager()

    owner = models.ForeignKey(User, null=True, blank=True)
    nowa = models.BooleanField(default=False)
    name = models.CharField(max_length=255, null=True)
    galaxy = models.ForeignKey(Galaxy)
    luna = models.ForeignKey(Lunas, null=True)
    last_update = models.FloatField(default=0)
    planet_type = models.IntegerField(max_length=11, default=1)
    destroyed = models.IntegerField(max_length=11, default=0)
    image = models.CharField(max_length=32, default='normaltempplanet01')
    points_builds = models.FloatField(default=0)
    points_flota = models.FloatField(default=0)
    points_tech = models.FloatField(default=0)
    points_obrona = models.FloatField(default=0)
    powierzchnia_zajeta = models.IntegerField(max_length=11, default=0)
    powierzchnia_max = models.IntegerField(max_length=11, default=0)
    powierzchnia_podstawowa = models.IntegerField(max_length=11, default=0)
    temp_min = models.IntegerField(max_length=3, default= -17)
    temp_max = models.IntegerField(max_length=3, default=23)
    metal = models.FloatField(default=0)
    metal_perhour = models.FloatField(default=0)
    metal_max = models.IntegerField(max_length=255, default=10000)
    crystal = models.FloatField(default=0)
    crystal_perhour = models.FloatField(default=0)
    crystal_max = models.IntegerField(max_length=255, default=10000)
    deuter = models.FloatField(default=0)
    deuter_perhour = models.FloatField(default=0)
    deuter_max = models.IntegerField(max_length=255, default=1000)
    energy_used = models.FloatField(default=0)
    energy_max = models.FloatField(default=0)
    terraformer_fields = models.IntegerField(max_length=255, default=0)
    ally_deposit = models.IntegerField(max_length=255, default=0)
    kolej = models.IntegerField(max_length=11, default=0)

    class Meta:
        app_label = APP_LABEL
        ordering = ('kolej', 'name', 'id')

    def zajety_budowaniem(self):
            if Budynki_f.objects.filter(planeta=self, time__gte=time()).count() > 0:
                obj = Budynki_f.objects.filter(planeta=self, time__gte=time()).order_by("time")[0]
                return {"nazwa": obj.budynek.nazwa, "sekundy": int(obj.time - time())}
            return None

    def zajety_badaniem(self):
        if Badania_f.objects.filter(planeta=self, time__gte=time()).count() > 0:
            obj = Badania_f.objects.filter(planeta=self, time__gte=time()).order_by("time")[0]
            return {"nazwa": obj.badanie.nazwa, "sekundy": int(obj.time - time())}
        return None

    def zajety_obrona(self):
        if Obrona_f.objects.filter(planeta=self, time__gte=time()).count() > 0:
            obj = Obrona_f.objects.filter(planeta=self, time__gte=time()).order_by("time")[0]
            nazwa = "%s: %s" % (obj.budynek.nazwa, obj.ilosc)
            return {"nazwa": nazwa, "sekundy": int(obj.time - time())}
        return None

    def zajety_flota(self):
        if Flota_f.objects.filter(planeta=self, time__gte=time()).count() > 0:
            obj = Flota_f.objects.filter(planeta=self, time__gte=time()).order_by("time")[0]
            nazwa = "%s: %s" % (obj.budynek.nazwa, obj.ilosc)
            return {"nazwa": nazwa, "sekundy": int(obj.time - time())}
        return None

    def get_procent_producji(self):
        procenty = 0
        ilosc = 0

        query = Budynki_p.objects.filter(planeta=self, budynek__czy_produkcja__gt=0)
        tmp = query.aggregate(suma=models.Sum("procent"))
        if tmp['suma'] > 0:
            procenty += tmp['suma']
        ilosc += query.count()

        query = Flota_p.objects.filter(planeta=self, budynek__czy_produkcja__gt=0)
        tmp = query.aggregate(suma=models.Sum("procent"))
        if tmp['suma'] > 0:
            procenty += tmp['suma']
        ilosc += query.count()

        try:
            return int(procenty / ilosc)
        except:
            return 0


class UserProfile(models.Model):
    objects = models.Manager()
    SEX = (
             ("M", "męska"),
             ("Z", "żeńska"),
             )

    authlevel = models.SmallIntegerField()

    sex = models.CharField(max_length=1, choices=SEX, null=True, blank=True, verbose_name='Płeć')
    miasto = models.CharField(max_length=255, null=True, blank=True, verbose_name="Zamieszkały w")
    data_urodzenia = models.DateField(null=True, blank=True, verbose_name="Data urodzenia\n<br> (2006-10-26, 10/25/2006)")
    avatar = models.ImageField(upload_to='avatar', null=True, blank=True)
    sign = models.TextField(verbose_name='Opis', null=True, blank=True)
    podglad_flota = models.BooleanField(default=True)
    nowe_raporty = models.IntegerField(default=0)

    current_planet = models.ForeignKey(Planets)
    user_lastip = models.CharField(max_length=16)
    onlinetime = models.IntegerField(max_length=11)
    noipcheck = models.SmallIntegerField(max_length=4)
    points_tech = models.FloatField(default=0)
    points = models.FloatField(default=0)
    points_flota = models.FloatField(default=0)
    points_builds = models.FloatField(default=0)
    points_obrona = models.FloatField(default=0)
    rank = models.IntegerField(max_length=11, default=0)
    new_message = models.IntegerField(max_length=11, default=0)
    ally_id = models.IntegerField(max_length=11, default=0)
    ally_name = models.CharField(max_length=32, default='')
    ally_request = models.IntegerField(max_length=11, default=0)
    ally_rank_id = models.IntegerField(max_length=11, default=0)
    ally_request_text = models.TextField()
    ally_register_time = models.IntegerField(max_length=11, default=0)
    current_luna = models.ForeignKey(Lunas, null=True)
    kolorminus = models.CharField(max_length=11, default='red')
    kolorplus = models.CharField(max_length=11, default='#00FF00')
    kolorpoziom = models.CharField(max_length=11, default='yellow')
    rank_old = models.IntegerField(max_length=11, default=0)
    user = models.OneToOneField(User, primary_key=True)
    fast_fleet = models.ManyToManyField(Planets, related_name="userprofile_fast_fleet")

    class Meta:
        app_label = APP_LABEL

    def get_alliance(self):
        try:
            return Sojusz.objects.get(czlonkowie__user=self.user)
        except Sojusz.DoesNotExist:
            pass
        return None


class Budynki_p(models.Model):
    objects = models.Manager()
    budynek = models.ForeignKey(Buildings)
    planeta = models.ForeignKey(Planets)
    ilosc = models.IntegerField(max_length=255, default=0)
    level = models.IntegerField(max_length=11, default=0)
    procent = models.IntegerField(max_length=11, default=100)

    class Meta:
        app_label = APP_LABEL


class Budynki_f(models.Model):
    objects = models.Manager()
    budynek = models.ForeignKey(Buildings)
    planeta = models.ForeignKey(Planets)
    level = models.IntegerField(max_length=11, default=0)
    points = models.FloatField(default=0)
    time = models.FloatField()
    czas_start = models.FloatField()

    class Meta:
        app_label = APP_LABEL


class Badania_p(models.Model):
    objects = models.Manager()
    badanie = models.ForeignKey(Badania)
    user = models.ForeignKey(User)
    level = models.IntegerField(max_length=11, default=0)

    class Meta:
        app_label = APP_LABEL


class Badania_f(models.Model):
    objects = models.Manager()
    badanie = models.ForeignKey(Badania)
    user = models.ForeignKey(User)
    planeta = models.ForeignKey(Planets)
    level = models.IntegerField(max_length=11, default=0)
    time = models.FloatField()
    points = models.FloatField(default=0)

    class Meta:
        app_label = APP_LABEL


class Flota(models.Model):
    objects = models.Manager()
    nazwa = models.CharField(max_length=255)
    opis = models.TextField()
    opis_dlugi = models.TextField()
    opis_dodatkowy = models.TextField()
    c_met = models.IntegerField(max_length=11)
    c_cry = models.IntegerField(max_length=11)
    c_deu = models.IntegerField(max_length=11)
    c_ene = models.IntegerField(max_length=11)
    c_czas = models.IntegerField(max_length=11)
    c_consumption = models.IntegerField(max_length=11)
    c_factor = models.FloatField()
    speed = models.IntegerField(max_length=11)
    speed_bad = models.ForeignKey(Badania, null=True, blank=True)
    capacity = models.IntegerField(max_length=11)
    bak = models.IntegerField(max_length=11)
    shield = models.IntegerField(max_length=11)
    attack = models.IntegerField(max_length=11)
    sd_flota = models.CharField(max_length=255)
    sd_obrona = models.CharField(max_length=255)
    met = models.IntegerField(max_length=11)
    cry = models.IntegerField(max_length=11)
    deu = models.IntegerField(max_length=11)
    ene = models.IntegerField(max_length=11)
    factor = models.FloatField()
    met_formula = models.CharField(max_length=255)
    cry_formula = models.CharField(max_length=255)
    deu_formula = models.CharField(max_length=255)
    ene_formula = models.CharField(max_length=255)
    czy_produkcja = models.IntegerField(max_length=5, default=0)
    w_bud = models.CharField(max_length=255)
    w_bad = models.CharField(max_length=255)
    id_old = models.IntegerField(max_length=11)
    kolonizacja = models.IntegerField(max_length=1, default=0)
    recycler = models.BooleanField(default=False)
    spy = models.BooleanField(default=False)
    lata = models.IntegerField(max_length=1, default=0)

    class Meta:
        app_label = APP_LABEL


class Flota_p(models.Model):
    objects = models.Manager()
    planeta = models.ForeignKey(Planets)
    budynek = models.ForeignKey(Flota)
    level = models.IntegerField(max_length=255, default=0)
    ilosc = models.IntegerField(max_length=255, default=0)
    procent = models.IntegerField(max_length=11, default=100)

    class Meta:
        app_label = APP_LABEL


class Flota_f(models.Model):
    objects = models.Manager()
    budynek = models.ForeignKey(Flota)
    planeta = models.ForeignKey(Planets)
    ilosc = models.IntegerField(max_length=255)
    points = models.FloatField(default=0)
    time_one = models.FloatField()
    time = models.FloatField()

    class Meta:
        app_label = APP_LABEL


class Fleets(models.Model):
    objects = models.Manager()
    fleet_owner = models.ForeignKey(User)
    fleet_mission = models.IntegerField(max_length=11, default=0)
    fleet_amount = models.IntegerField(max_length=11, default=0)
    fleet_array = models.TextField()

    time_start = models.FloatField(default=0)
    time = models.FloatField(default=0)

    galaxy_start = models.ForeignKey(Galaxy, related_name="fleets_galaxy_start")
    galaxy_end = models.ForeignKey(Galaxy, related_name="fleets_galaxy_end")

    fleet_resource_metal = models.IntegerField(max_length=11, default=0)
    fleet_resource_crystal = models.IntegerField(max_length=11, default=0)
    fleet_resource_deuterium = models.IntegerField(max_length=11, default=0)
    fleet_back = models.IntegerField(max_length=11, default=0)
    bak = models.IntegerField(max_length=11, default=0)

    class Meta:
        app_label = APP_LABEL


class Lang(models.Model):
    objects = models.Manager()
    number = models.IntegerField(max_length=32, default=0)
    type = models.CharField(max_length=11)
    text = models.CharField(max_length=255)

    class Meta:
        app_label = APP_LABEL


class Tematy(models.Model):
    objects = models.Manager()
    nadawca = models.ForeignKey(User)
    odbiorca = models.ForeignKey(User, related_name='o_user')
    n_del = models.CharField(max_length=1, choices=TAK_NIE)
    o_del = models.CharField(max_length=1, choices=TAK_NIE)
    n_prz = models.CharField(max_length=1, choices=TAK_NIE, default='N')
    o_prz = models.CharField(max_length=1, choices=TAK_NIE, default='N')
    temat = models.TextField()
    data = models.DateTimeField()

    class Meta:
        app_label = APP_LABEL


class Wiadomosci(models.Model):
    objects = models.Manager()
    temat = models.ForeignKey(Tematy)
    tekst = models.TextField()
    kto = models.ForeignKey(User)
    data = models.DateTimeField()

    class Meta:
        app_label = APP_LABEL


class Bany(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User)
    do = models.DateTimeField()
    powod = models.TextField()

    class Meta:
        app_label = APP_LABEL


class TematyMod(models.Model):
    objects = models.Manager()
    powod = models.TextField()
    kto_raportowal = models.ForeignKey(User)
    nadawca = models.ForeignKey(User, related_name='n_user_mod')
    odbiorca = models.ForeignKey(User, related_name='o_user_mod')
    temat = models.TextField()
    data = models.DateTimeField()
    ban = models.ForeignKey(Bany, null=True, blank=True)
    uzasadnienie = models.TextField()
    rozpatrzony = models.BooleanField(default=False)

    class Meta:
        app_label = APP_LABEL


class WiadomosciMod(models.Model):
    objects = models.Manager()
    temat = models.ForeignKey(TematyMod)
    tekst = models.TextField()
    kto = models.ForeignKey(User)
    data = models.DateTimeField()

    class Meta:
        app_label = APP_LABEL


class Obrona(models.Model):
    objects = models.Manager()
    nazwa = models.CharField(max_length=255)
    opis = models.TextField()
    opis_dlugi = models.TextField()
    opis_dodatkowy = models.TextField()
    c_met = models.IntegerField(max_length=11)
    c_cry = models.IntegerField(max_length=11)
    c_deu = models.IntegerField(max_length=11)
    c_ene = models.IntegerField(max_length=11)
    c_czas = models.IntegerField(max_length=11)
    c_consumption = models.IntegerField(max_length=11)
    c_factor = models.FloatField()
    speed = models.IntegerField(max_length=11)
    capacity = models.IntegerField(max_length=11)
    shield = models.IntegerField(max_length=11)
    attack = models.IntegerField(max_length=11)
    sd_flota = models.CharField(max_length=255)
    sd_obrona = models.CharField(max_length=255)
    met = models.IntegerField(max_length=11)
    cry = models.IntegerField(max_length=11)
    deu = models.IntegerField(max_length=11)
    ene = models.IntegerField(max_length=11)
    factor = models.FloatField()
    met_formula = models.CharField(max_length=255)
    cry_formula = models.CharField(max_length=255)
    deu_formula = models.CharField(max_length=255)
    ene_formula = models.CharField(max_length=255)
    czy_produkcja = models.IntegerField(max_length=5, default=0)
    w_bud = models.CharField(max_length=255)
    w_bad = models.CharField(max_length=255)
    limit = models.IntegerField(max_length=2)
    id_old = models.IntegerField(max_length=11)

    class Meta:
        app_label = APP_LABEL


class Obrona_p(models.Model):
    objects = models.Manager()
    planeta = models.ForeignKey(Planets)
    budynek = models.ForeignKey(Obrona)
    level = models.IntegerField(max_length=255, default=0)
    ilosc = models.IntegerField(max_length=255, default=0)
    procent = models.IntegerField(max_length=11, default=100)

    class Meta:
        app_label = APP_LABEL


class Obrona_f(models.Model):
    objects = models.Manager()
    budynek = models.ForeignKey(Obrona)
    planeta = models.ForeignKey(Planets)
    ilosc = models.IntegerField(max_length=255)
    points = models.FloatField(default=0)
    time_one = models.FloatField(default=0)
    time = models.FloatField()
    anulowanie = models.BooleanField(default=True)

    class Meta:
        app_label = APP_LABEL


class Sojusz(models.Model):
    objects = models.Manager()
    nazwa = models.CharField(max_length=255, unique=True)
    profil = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to='photo', null=True, blank=True)
    text_wewn = models.TextField(null=True, blank=True)
    # zalozyciel = models.OneToOneField(User,db_column="zalozyciel_id")

    class Meta:
        app_label = APP_LABEL


class Czlonkowie(models.Model):
    objects = models.Manager()
    user = models.OneToOneField(User, db_column='user_id')
    sojusz = models.ForeignKey(Sojusz, db_column='sojusz_id')
    data = models.DateTimeField(auto_now_add=True)
    tytul = models.CharField(max_length=255, null=True, blank=True)
    wlasciciel = models.BooleanField(default=False)
    zmiana_opisu = models.BooleanField(default=False)
    wysylanie_zaproszen = models.BooleanField(default=False)
    wyrzucanie = models.BooleanField(default=False)

    class Meta:
        app_label = APP_LABEL


class Zaproszenia(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User)
    sojusz = models.ForeignKey(Sojusz)
    od = models.ForeignKey(User, related_name='od_zaproszenia')
    data = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        app_label = APP_LABEL


class SojuszChat(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User)
    sojusz = models.ForeignKey(Sojusz)
    wiadomosc = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = APP_LABEL
        ordering = ("id",)


class GalaxyFree(models.Model):
    objects = models.Manager()
    field = models.IntegerField()
    system = models.IntegerField()
    galaxy = models.IntegerField()

    class Meta:
        app_label = APP_LABEL


class SojuszLog(models.Model):
    objects = models.Manager()
    sojusz = models.ForeignKey(Sojusz)
    tekst = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = APP_LABEL


class Rynek(models.Model):
    objects = models.Manager()
    planeta = models.ForeignKey(Planets)
    data = models.DateTimeField(auto_now_add=True)
    co = models.CharField(max_length=1, choices=SUROWCE, verbose_name="Sprzedaje")
    co_ile = models.IntegerField(max_length=11, verbose_name="Sprzedawana ilość")
    na = models.CharField(max_length=1, choices=SUROWCE, verbose_name="Kupuje")
    na_ile = models.IntegerField(max_length=11, verbose_name="Kupowana ilość")
    ilosc = models.IntegerField(max_length=11, verbose_name="Ilość paczek")
    ratio = models.FloatField()

    class Meta:
        app_label = APP_LABEL


class StareMaile(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User, null=True, blank=True)
    email = models.EmailField()

    class Meta:
        app_label = APP_LABEL


class ZmianaHasla(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User)
    haslo = models.CharField(max_length=255)
    hash = models.CharField(max_length=40, db_index=True)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = APP_LABEL


class ZmianaMaila(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User)
    email = models.EmailField()
    hash = models.CharField(max_length=40, db_index=True)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = APP_LABEL

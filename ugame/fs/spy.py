# -*- coding: utf-8 -*-
from __future__ import division
from math import floor,pow,sqrt
from string import find,split
from time import time

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from functions import check_active
from fun_jinja import jrender_response


from game.models import *
import game.funkcje as fun
from game.topnav import topnav_site
from settings import GAME_SPEED,RES_SPEED,MAX_GALAXY,MAX_PLANETA,MAX_SYSTEM,FLEET_SPEED


from django.db import connection, backend, models

class Output:pass



@check_active
def spy(request):
    GraObject = request.GameObj
    current_planet = GraObject.get_current_planet()
    
    dane = Output()
    try:
        dane.planeta_id = int(request.REQUEST['p'])
        dane.system_id = int(request.REQUEST['s'])
        dane.galaktyka_id = int(request.REQUEST['g'])
        if 'ship_request' in request.session:del request.session['ship_request']
    except:
        if 'planeta_dane' in request.session:
            dane=request.session['planeta_dane']
        else:
            return HttpResponseRedirect("/game/galaxy/")
    if not fun.check_is_planet(GraObject.user, dane.planeta_id, dane.system_id, dane.galaktyka_id):
        return HttpResponseRedirect("/game/galaxy/")
    if 'ship_request' in request.session:
        ship_request = request.session['ship_request']
        if not request.REQUEST.has_key("cp"):del request.session['ship_request']
    else:ship_request=None
    
    if fun.is_planet_owner(GraObject.user, dane,True):
        return HttpResponseRedirect("/game/galaxy/")
    
    topnav = topnav_site(GraObject)
    
    dostepne_statki_tmp = Flota_p.objects.values_list('budynek_id',flat=True).filter(planeta=current_planet,budynek__lata__gt=0,ilosc__gt=0).order_by("budynek")
    dostepne_statki = []
    for i in dostepne_statki_tmp:
        d=Output()
        statek = GraObject.cache_obj.get_flota_p(current_planet.pk,i)
        d.nazwa=statek.budynek.nazwa
        d.ilosc = statek.ilosc
        d.pk = statek.pk
        d.speed = int(fun.get_speed(GraObject,statek.budynek,GraObject.user))
        if ship_request:
            try:
                d.value=int(ship_request[d.budynek_id])
            except:
                d.value=0
        else:
            d.value=0
        dostepne_statki.append(d)
    
    request.session['planeta_dane']=dane
    return jrender_response(request,'game/fs_spy.html',{"dane":dane,'topnav':topnav,"dostepne_statki":dostepne_statki})


@check_active
def spy_1(request):
    GraObject = request.GameObj
    current_planet = GraObject.get_current_planet()
    
    if 'planeta_dane' in request.session:
        planeta_dane = request.session['planeta_dane']
    else:
        return HttpResponseRedirect("/game/overview/")
    
    try:
        if request.REQUEST.has_key('speed'):
            test = float(request.REQUEST['speed'])
            planeta_dane.speed_procent = test
        if not planeta_dane.speed_procent>=1.0 or not planeta_dane.speed_procent<=10.0:
            planeta_dane.speed_procent=10.0
    except:
        return HttpResponseRedirect("/game/fs/spy/")
    
    if not fun.check_is_planet(GraObject.user, planeta_dane.planeta_id, planeta_dane.system_id, planeta_dane.galaktyka_id):
        return HttpResponseRedirect("/game/galaxy/")
    
    if fun.is_planet_owner(GraObject.user, planeta_dane,True):
        return HttpResponseRedirect("/game/galaxy/")
    
    
    if 'id_statkow' in request.session:
        id_statkow=request.session['id_statkow']
    else:
        id_statkow=None
    if 'ship_request' in request.session:
        ship_request=request.session['ship_request']
    else:
        ship_request=None
    
    if not id_statkow or not ship_request:
        tmp = fun.get_ship_request(GraObject,current_planet, request, GraObject.user,planeta_dane)
    else:
        tmp = fun.get_ship_request(GraObject,current_planet, request, GraObject.user,planeta_dane,False,False,False)
    
    if not tmp:
        if not id_statkow or not ship_request:
            return HttpResponseRedirect("/game/fs/spy/")
        else:
            tmp = fun.check_ship_request(GraObject,request,current_planet,planeta_dane,id_statkow, ship_request, GraObject.user)
            if not tmp:
                return HttpResponseRedirect("/game/fs/spy/")
    
    id_statkow=tmp['id_statkow']
    ship_request=tmp['ship_request']
    dane_floty=tmp['dane_floty']
    statki_podsumowanie=tmp['statki_podsumowanie']
    
    dane_floty.odleglosc = fun.odleglosc(current_planet, planeta_dane.galaktyka_id, planeta_dane.system_id, planeta_dane.planeta_id)
    dane_floty.czas_lotu = fun.getCzasLotu(planeta_dane.speed_procent,dane_floty.speed, dane_floty.odleglosc, FLEET_SPEED)
    dane_floty.zuzycie_deuter =  fun.get_zuzycie_deuteru(dane_floty,planeta_dane)
            
    if dane_floty.bak_pojemnosc-dane_floty.zuzycie_deuter<0:
        GraObject.user.message_set.create(message="Nie można zabrać wystarczająco paliwa. Pojemność baków:"+str(dane_floty.bak_pojemnosc)+", potrzeba:"+str(dane_floty.zuzycie_deuter))
        return HttpResponseRedirect("/game/fs/spy/")
    if dane_floty.zuzycie_deuter>current_planet.deuter:
        GraObject.user.message_set.create(message="Masz za mało deuteru na planecie")
        return HttpResponseRedirect("/game/fs/spy/")
    
    request.session['planeta_dane']=planeta_dane
    request.session['dane_floty']=dane_floty
    request.session['ship_request']=ship_request
    request.session['id_statkow']=id_statkow
    
    
    topnav = topnav_site(GraObject)
    return jrender_response(request,'game/fs_spy_podsumowanie.html',{"planeta_dane":planeta_dane,"dane_floty":dane_floty,'topnav':topnav,"statki_podsumowanie":statki_podsumowanie})


@check_active
def spy_2(request):
    GraObject = request.GameObj
    current_planet = GraObject.get_current_planet()
    
    if 'planeta_dane' in request.session:
        planeta_dane = request.session['planeta_dane']
    else:
        return HttpResponseRedirect("/game/overview/")
    if 'id_statkow' in request.session:
        id_statkow=request.session['id_statkow']
    else:
        return HttpResponseRedirect("/game/overview/")
    if 'ship_request' in request.session:
        ship_request=request.session['ship_request']
    else:
        return HttpResponseRedirect("/game/overview/")
    
    if not fun.check_is_planet(GraObject.user, planeta_dane.planeta_id, planeta_dane.system_id, planeta_dane.galaktyka_id):
        return HttpResponseRedirect("/game/galaxy/")
    
    if fun.is_planet_owner(GraObject.user, planeta_dane,True):
        return HttpResponseRedirect("/game/galaxy/")
    
    
    tmp = fun.check_ship_request(GraObject,request,current_planet,planeta_dane,id_statkow, ship_request, GraObject.user)
    if not tmp:
        return HttpResponseRedirect("/game/overview/")
    dane_floty=tmp['dane_floty']
    id_statkow=tmp['id_statkow']
    ship_request=tmp['ship_request']
    
    
    dane_floty.odleglosc = fun.odleglosc(current_planet, planeta_dane.galaktyka_id, planeta_dane.system_id, planeta_dane.planeta_id)
    dane_floty.czas_lotu = fun.getCzasLotu(planeta_dane.speed_procent,dane_floty.speed, dane_floty.odleglosc, FLEET_SPEED)
    dane_floty.zuzycie_deuter =  fun.get_zuzycie_deuteru(dane_floty,planeta_dane)
            
    if dane_floty.bak_pojemnosc-dane_floty.zuzycie_deuter<0:
        GraObject.user.message_set.create(message="Nie można zabrać wystarczająco paliwa. Pojemność baków:"+str(dane_floty.bak_pojemnosc)+", potrzeba:"+str(dane_floty.zuzycie_deuter))
        return HttpResponseRedirect("/game/fs/spy/")
    if dane_floty.zuzycie_deuter>current_planet.deuter:
        GraObject.user.message_set.create(message="Masz za mało deuteru na planecie")
        return HttpResponseRedirect("/game/fs/spy/")

    
    current_planet.deuter -= dane_floty.zuzycie_deuter
    
    
    
    fleet_array = []
    fleet_amount = 0
    for i in id_statkow:
        fleet_array.append("%s,%s" % (i,ship_request[i]))
        fleet_amount += int(ship_request[i])
        statek_row = GraObject.cache_obj.get_flota_p(current_planet.pk,int(i))
        statek_row.ilosc -= int(ship_request[i])
    time_start = time()
    
    galaxy_end = Galaxy.objects.get(galaxy=planeta_dane.galaktyka_id,system=planeta_dane.system_id,field=planeta_dane.planeta_id)
    
    flota_row = Fleets.objects.create(fleet_owner=GraObject.user,fleet_mission=6,fleet_amount=fleet_amount,fleet_array=";".join(fleet_array),time_start=time_start,
                       galaxy_start=current_planet.galaxy,
                       time=time_start+dane_floty.czas_lotu,
                       galaxy_end=galaxy_end,
                       fleet_resource_metal=0,fleet_resource_crystal=0,fleet_resource_deuterium=0,bak=dane_floty.zuzycie_deuter)
        
    del request.session['id_statkow']
    del request.session['ship_request']
    del request.session['planeta_dane']
    return HttpResponseRedirect("/game/fleet/")

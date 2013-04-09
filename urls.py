# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *  # @UnusedWildImport
from settings import MEDIA_ROOT, MEDIA_STATIC_ROOT
urlpatterns = patterns('',

     (r'^cms/', include('cms.urls')),
     (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
     (r'^media_static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_STATIC_ROOT}),

)

from ugame.cms_controller import controller as ugame_control
ugame_control.get_modules()
urlpatterns += ugame_control.get_urls()


"""
# TODO: reimplement
# (r'favicon.ico', 'game.funkcje.icon'),
# (r'^accounts/', include('registration.urls')),

(r'^change_email/(?P<activation_key>\w+)/$', 'game.user.change_email'),
(r'^change_pass/(?P<activation_key>\w+)/$', 'game.user.change_pass'),


(r'^game/handlarz/(?P<page>[0-9]*)/$', 'game.handlarz.main'),
(r'^game/handlarz/$', 'game.handlarz.main'),

(r'^game/handlarz/handel_main/$', 'game.handlarz.handel_main'),
(r'^game/handlarz/handel/$', 'game.handlarz.handel'),
(r'^game/handlarz/rynek/$', 'game.handlarz.rynek'),
(r'^game/handlarz/rynek_wystaw/(?P<page>[0-9]*)/$', 'game.handlarz.rynek_wystaw'),
(r'^game/handlarz/rynek_wystaw/$', 'game.handlarz.rynek_wystaw'),

(r'^game/usr/$', 'game.user.profile_edit'),
(r'^game/usr/(?P<id>[0-9]*)/$', 'game.user.profile'),

(r'^game/sojusz/dolacz/(?P<id>[0-9]*)/$', 'game.sojusz.dolacz'),
(r'^game/sojusz/odrzuc/(?P<id>[0-9]*)/$', 'game.sojusz.odrzuc'),

(r'^game/sojusz/uprawnienia/(?P<id>[0-9]*)/$', 'game.sojusz.uprawnienia'),
(r'^game/sojusz/wyslij_zaproszenie/(?P<id>[0-9]*)/$', 'game.sojusz.wyslij_zaproszenie'),
(r'^game/sojusz/zaproszenia/$', 'game.sojusz.zaproszenia'),
(r'^game/sojusz/czlonkowie/$', 'game.sojusz.czlonkowie'),
(r'^game/sojusz/zaloz/$', 'game.sojusz.zaloz'),
(r'^game/sojusz/przeglad/$', 'game.sojusz.przeglad'),
(r'^game/sojusz/opusc/$', 'game.sojusz.opusc'),
(r'^game/sojusz/chat/$', 'game.sojusz.chat'),
(r'^game/sojusz/chat/get/$', 'game.sojusz.chat_get'),
(r'^game/sojusz/chat/send/$', 'game.sojusz.chat_send'),


(r'^game/sojusz/profil_edytuj/$', 'game.sojusz.profil_edytuj'),
(r'^game/sojusz/profil/$', 'game.sojusz.profil'),
(r'^game/sojusz/$', 'game.sojusz.main'),
(r'^game/sojusz_podglad/(?P<id>[0-9]*)/$', 'game.sojusz.podglad'),

(r'^game/regulamin/$', 'main.views.regulamin'),

# (r'^game/stats/flota/(?P<page>[0-9]*)/$', 'game.stats.flota'),
(r'^game/stats/(?P<page>[0-9]*)/$', 'game.stats.main'),
(r'^game/stats/$', 'game.stats.main'),


(r'^game/leftmenu/$', 'game.views.leftmenu'),
(r'^game/overview/$', 'game.overview.overview'),
(r'^game/main/$', 'game.views.main'),
(r'^game/buildings/$', 'game.buildings.main'),
(r'^game/tech/$', 'game.tech.main'),

(r'^game/raporty/$', 'game.raporty.main'),
(r'^game/raporty/(?P<id>[0-9]*)/$', 'game.raporty.main'),

(r'^game/fleet/$', 'game.fleet.main'),
(r'^game/flota/$', 'game.flota.main'),
(r'^game/obrona/$', 'game.obrona.main'),
(r'^game/imperium_kolej/$', 'game.imperium.kolej_planet'),
(r'^game/imperium/$', 'game.imperium.main'),
(r'^game/techtree/$', 'game.techtree.main'),
(r'^game/resources/$', 'game.resources.main'),
(r'^game/hidden/$', 'game.hidden.main'),
(r'^game/cron/$', 'game.hidden.cron'),
(r'^game/free/$', 'game.hidden.check_free'),

(r'^game/wiadomosc/raport/(?P<id>[0-9]*)/$', 'game.wiadomosci.raport'),
(r'^game/messages/$', 'game.wiadomosci.lista'),
(r'^game/message/(?P<id>[0-9]*)/$', 'game.wiadomosci.wiadomosc'),
(r'^game/mes_del/(?P<id>[0-9]*)/$', 'game.wiadomosci.wiadomosc_usun'),
(r'^game/compose/$', 'game.wiadomosci.komponuj'),
(r'^game/compose/(?P<id>.*)/$', 'game.wiadomosci.komponuj'),



(r'^game/fs/', include('game.fs.urls')),



(r'^game/galaxy/(?P<galaxy>.*)/(?P<system>.*)/$', 'game.galaxy.main'),
(r'^game/galaxy/$', 'game.galaxy.main'),

(r'^game/info/bud/(?P<id>[0-9]*)/$', 'game.info.budynki'),
(r'^game/info/bad/(?P<id>[0-9]*)/$', 'game.info.badania'),
(r'^game/info/flo/(?P<id>[0-9]*)/$', 'game.info.flota'),
(r'^game/info/obr/(?P<id>[0-9]*)/$', 'game.info.obrona'),

(r'^game/$', 'game.views.main'),
(r'^game/main/favicon.ico', 'game.funkcje.icon'),
(r'^favicon.ico', 'game.funkcje.icon'),
(r'^game/favicon.ico', 'game.funkcje.icon'),
(r'^$', 'main.views.main'),

"""

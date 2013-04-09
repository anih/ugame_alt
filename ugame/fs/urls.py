# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from settings import DEBUG, MEDIA_ROOT
urlpatterns = patterns('',
     (r'^kolonizuj/$', 'game.fs.kolonizuj.kolonizuj'),
     (r'^kolonizuj/1/$', 'game.fs.kolonizuj.kolonizuj_1'),
     (r'^kolonizuj/2/$', 'game.fs.kolonizuj.kolonizuj_2'),
     
     
     (r'^przeslij/$', 'game.fs.przeslij.przeslij'),
     (r'^przeslij/1/$', 'game.fs.przeslij.przeslij_1'),
     (r'^przeslij/2/$', 'game.fs.przeslij.przeslij_2'),
     
     (r'^surowce/$', 'game.fs.surowce.surowce'),
     (r'^surowce/1/$', 'game.fs.surowce.surowce_1'),
     (r'^surowce/2/$', 'game.fs.surowce.surowce_2'),
     
     (r'^atak/$', 'game.fs.atak.atak'),
     (r'^atak/1/$', 'game.fs.atak.atak_1'),
     (r'^atak/2/$', 'game.fs.atak.atak_2'),
     
     (r'^zlom/$', 'game.fs.zlom.zlom'),
     (r'^zlom/1/$', 'game.fs.zlom.zlom_1'),
     (r'^zlom/2/$', 'game.fs.zlom.zlom_2'),
     
     (r'^spy/$', 'game.fs.spy.spy'),
     (r'^spy/1/$', 'game.fs.spy.spy_1'),
     (r'^spy/2/$', 'game.fs.spy.spy_2'),
)

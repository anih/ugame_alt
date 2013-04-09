# -*- coding: utf-8 -*-
from __future__ import division
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
import django.forms as forms
import ugame.models as m
# Create the form class.


class RaportujTemat(forms.Form):
    powod = forms.CharField(widget=forms.Textarea(), label="Powód", required=True)


class UprawnieniaForm(forms.ModelForm):
    class Meta:
        model = m.Czlonkowie
        fields = ("tytul", "wlasciciel", "zmiana_opisu", "wysylanie_zaproszen", "wyrzucanie",)
        # exclude=('user','sojusz','od','data')


class ZaproszenieForm(forms.ModelForm):
    class Meta:
        model = m.Zaproszenia
        fields = ("text",)
        # exclude=('user','sojusz','od','data')

SUROWCE = (
           ("-", "--wybierz--"),
           ("M", "Metal"),
           ("K", "Kryształ"),
           ("D", "Deuter"),
           )

class SojuszForm(forms.ModelForm):
    class Meta:
        model = m.Sojusz
        exclude = ('zalozyciel')


class UserprofileForm(forms.ModelForm):
    class Meta:
        model = m.UserProfile
        fields = ('sex', 'miasto', 'data_urodzenia', 'avatar', 'sign')

class ChangePassMail(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(maxlength=75)), label=_(u'email address'), required=False)
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_(u'password'), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_(u'password (again)'), required=False)


class RynekSearch(forms.Form):
    co = forms.ChoiceField(choices=SUROWCE, required=False)
    na = forms.ChoiceField(choices=SUROWCE, required=False)

class RynekForm(forms.ModelForm):

    class Meta:
        model = m.Rynek
        exclude = ('data', 'planeta', 'ratio')


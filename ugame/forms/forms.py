# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import django.forms as forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

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
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(maxlength=75)), label=_(u'email address'),
                             required=False)
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_(u'password'), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_(u'password (again)'),
                                required=False)


class RynekSearch(forms.Form):
    co = forms.ChoiceField(choices=SUROWCE, required=False)
    na = forms.ChoiceField(choices=SUROWCE, required=False)


class RynekForm(forms.ModelForm):
    class Meta:
        model = m.Rynek
        exclude = ('data', 'planeta', 'ratio')


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_email': "Ten adres jest już w naszej bazie.",
        'password_mismatch': _("The two password fields didn't match."),
    }

    first_name = forms.CharField(label="Imię", max_length=100)
    email = forms.EmailField(label="Adres e-mail", max_length=255)

    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("first_name", "email")

    def clean_email(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

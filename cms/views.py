# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from ugame.models import TematyMod, User, WiadomosciMod, Bany
from cms.funkcje import admin_required
import datetime
from django.core.urlresolvers import reverse
from django.contrib.auth import  login, logout, get_backends
from utils.jinja.fun_jinja import jrender


@admin_required
def login_other(request, user_id):
    user = request.user
    if user.is_superuser:
        print user.username
        for backend in get_backends():
            try:
                backend2 = backend
            except TypeError:
                continue

        new_user = User.objects.get(pk=user_id)
        new_user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)

        logout(request)

        login(request, new_user)
    return HttpResponseRedirect("/")



@admin_required
def wiadomosci_przeslane(request):
    wiadomosci = TematyMod.objects.filter(rozpatrzony=False)
    return jrender(request, "cms/wiadomosci/przeslane_lista.html", {"wiadomosci":wiadomosci})

@admin_required
def wiadomosc_przeslana(request, id):
    user = request.user
    try:
        temat = TematyMod.objects.get(pk=id, rozpatrzony=False)
    except:
        return HttpResponseRedirect(reverse("cms.views.wiadomosci_przeslane"))
    wiadomosci = WiadomosciMod.objects.filter(temat=temat).order_by("data")
    if request.method == 'POST':
        powod = request.POST.get('powod', '')
        if 'na_dni' in request.POST and 'ban_dla' in request.POST and len(powod) > 0:
            try:
                ban_dla = int(request.POST['ban_dla'])
                na_dni = int(request.POST['na_dni'])
            except:
                user.message_set.create(message="Podaj wszystkie dane")
                return HttpResponseRedirect(reverse("cms.views.wiadomosc_przeslana", kwargs={"id":temat.pk}))
            if na_dni == 0:
                temat.uzasadnienie = powod
                temat.rozpatrzony = True
                temat.save()
                user.message_set.create(message="Gracze zostali ułaskawieni")
                return HttpResponseRedirect(reverse("cms.views.wiadomosci_przeslane"))
            elif na_dni > 7 or na_dni < 1:
                user.message_set.create(message="Wybierz poprawną ilość dni")
                return HttpResponseRedirect(reverse("cms.views.wiadomosc_przeslana", kwargs={"id":temat.pk}))
            if ban_dla == temat.nadawca.pk:
                if not user.is_superuser and temat.nadawca.is_staff:
                    user.message_set.create(message="Nie jesteś adminem, więc nie możesz banować moderatorów")
                    return HttpResponseRedirect(reverse("cms.views.wiadomosc_przeslana", kwargs={"id":temat.pk}))
                ban = Bany.objects.create(user=temat.nadawca, do=datetime.datetime.now() + datetime.timedelta(days=na_dni), powod=powod)
                temat.ban = ban
                temat.uzasadnienie = powod
                temat.rozpatrzony = True
                temat.save()
            elif ban_dla == temat.odbiorca.pk:
                if not user.is_superuser and temat.odbiorca.is_staff:
                    user.message_set.create(message="Nie jesteś adminem, więc nie możesz banować moderatorów")
                    return HttpResponseRedirect(reverse("cms.views.wiadomosc_przeslana", kwargs={"id":temat.pk}))
                ban = Bany.objects.create(user=temat.odbiorca, do=datetime.datetime.now() + datetime.timedelta(days=na_dni), powod=powod)
                temat.ban = ban
                temat.uzasadnienie = powod
                temat.rozpatrzony = True
                temat.save()
            else:
                user.message_set.create(message="Wybierz właściwego gracza")
                return HttpResponseRedirect(reverse("cms.views.wiadomosc_przeslana", kwargs={"id":temat.pk}))
            user.message_set.create(message="Gracz został zbanowany")
            return HttpResponseRedirect(reverse("cms.views.wiadomosci_przeslane"))
        else:
            user.message_set.create(message="Podaj wszystkie dane")
    return jrender(request, "cms/wiadomosci/przeslana_wiecej.html", {"temat":temat, "wiadomosci":wiadomosci})


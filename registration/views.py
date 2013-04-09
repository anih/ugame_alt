"""
Views which allow users to create and activate accounts.

"""


from django.conf import settings
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import logout

from game.models import Planets, Galaxy, UserProfile, GalaxyFree
from settings import MAX_GALAXY, MAX_PLANETA, MAX_SYSTEM, MNOZNIK_MAGAZYNOW
from random import randint
from time import time

from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from django.db import connection, backend, models
from utils.jinja.fun_jinja import jrender_response

def logout_view(request):
    logout(request)
    return jrender_response("registration/logout.html", {})


def registration_complete(request):
    return jrender_response("registration/registration_complete.html", {})

def clean(request):
    from registration.models import RegistrationProfile
    del_users = RegistrationProfile.objects.delete_expired_users()
    return jrender_response("clean.html", {"del":del_users})

def activate(request, activation_key, template_name='registration/activate.html'):
    """
    Activates a ``User``'s account, if their key is valid and hasn't
    expired.
    
    By default, uses the template ``registration/activate.html``; to
    change this, pass the name of a template as the keyword argument
    ``template_name``.
    
    Context:
    
        account
            The ``User`` object corresponding to the account, if the
            activation was successful. ``False`` if the activation was
            not successful.
    
        expiration_days
            The number of days for which activation keys stay valid
            after registration.
    
    Template:
    
        registration/activate.html or ``template_name`` keyword
        argument.
    
    """
    activation_key = activation_key.lower()  # Normalize before trying anything with it.

    tmp_activ = RegistrationProfile.objects.activate_user(activation_key)
    if tmp_activ:
        account = tmp_activ[0]
        planet_name = tmp_activ[1]
    else:
        return jrender_response(template_name,
                              { 'account': tmp_activ,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS })
    test = Planets.objects.filter(owner=account).count()
    query = "lock table game_galaxy in ACCESS EXCLUSIVE MODE"
    cursor = connection.cursor()
    cursor.execute(query)
    if not test > 0:
        print "brak planety"

        max = Galaxy.objects.filter(planet__owner__isnull=True, planet__nowa=True).order_by("-id")[0].pk
        print "max" + str(max)
        rand = randint(1, int(max))
        print "rand:" + str(rand)
        if Galaxy.objects.filter(id__gte=rand, planet__owner__isnull=True, planet__nowa=True).count() > 0:
            galaxy_obj = Galaxy.objects.filter(id__gte=rand, planet__owner__isnull=True, planet__nowa=True)[0]
        else:
            galaxy_obj = Galaxy.objects.filter(id__lte=rand, planet__owner__isnull=True, planet__nowa=True).order_by("-id")[0]

        planeta = galaxy_obj.planet
        planet = galaxy_obj.field
        if planet == 1 or planet == 2 or planet == 3:
            powierzchnia_max = randint(150, 200)
            temp_min = randint(0, 100)
            temp_max = temp_min + randint(10, 40)
            image = "trockenplanet"
        elif planet == 4 or planet == 5 or planet == 6:
            powierzchnia_max = randint(200, 300)
            temp_min = randint(-25, 75)
            temp_max = temp_min + randint(10, 40)
            image = "dschjungelplanet"
        elif planet == 7 or planet == 8 or planet == 9:
            powierzchnia_max = randint(180, 250)
            temp_min = randint(-50, 50)
            temp_max = temp_min + randint(10, 40)
            image = "normaltempplanet"
        elif planet == 10 or planet == 11 or planet == 12:
            powierzchnia_max = randint(200, 250)
            temp_min = randint(-75, 25)
            temp_max = temp_min + randint(10, 40)
            image = "wasserplanet"
        else:
            powierzchnia_max = randint(180, 280)
            temp_min = randint(-100, 10)
            temp_max = temp_min + randint(10, 40)
            image = "eisplanet"
        planet_type = 1
        tmp = randint(1, 10)
        if tmp < 10:image = image + "0" + str(tmp)
        else: image = image + str(tmp)

        planeta.nowa = False
        planeta.last_update = time()
        planeta.planet_type = planet_type
        planeta.image = image
        planeta.powierzchnia_max = powierzchnia_max
        planeta.powierzchnia_podstawowa = powierzchnia_max
        planeta.powierzchnia_zajeta = 0
        planeta.temp_min = temp_min
        planeta.temp_max = temp_max
        planeta.metal = 500
        planeta.metal_max = 10000 * MNOZNIK_MAGAZYNOW
        planeta.crystal = 500
        planeta.crystal_max = 10000 * MNOZNIK_MAGAZYNOW
        planeta.deuter = 100
        planeta.deuter_max = 10000 * MNOZNIK_MAGAZYNOW
        planeta.name = planet_name
        planeta.owner = account
        planeta.save()

        userprofile = UserProfile.objects.create(authlevel=0, sex="M", avatar="", sign="", current_planet=planeta, user_lastip='', onlinetime=0, noipcheck=0,
                                                 points_tech=0, points=0, rank=0, new_message=0, ally_request_text='', user=account)
        # account.current_planet = planet_obj
        # account.save()
    return jrender_response(template_name,
                              { 'account': account,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS })


def register(request, success_url='/accounts/register/complete/',
             form_class=RegistrationForm, profile_callback=None,
             template_name='registration/registration_form.html'):
    """
    Allows a new user to register an account.
    
    Following successful registration, redirects to either
    ``/accounts/register/complete/`` or, if supplied, the URL
    specified in the keyword argument ``success_url``.
    
    By default, ``registration.forms.RegistrationForm`` will be used
    as the registration form; to change this, pass a different form
    class as the ``form_class`` keyword argument. The form class you
    specify must have a method ``save`` which will create and return
    the new ``User``, and that method must accept the keyword argument
    ``profile_callback`` (see below).
    
    To enable creation of a site-specific user profile object for the
    new user, pass a function which will create the profile object as
    the keyword argument ``profile_callback``. See
    ``RegistrationManager.create_inactive_user`` in the file
    ``models.py`` for details on how to write this function.
    
    By default, uses the template
    ``registration/registration_form.html``; to change this, pass the
    name of a template as the keyword argument ``template_name``.
    
    Context:
    
        form
            The registration form.
    
    Template:
    
        registration/registration_form.html or ``template_name``
        keyword argument.
    
    """
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            new_user = form.save(profile_callback=profile_callback)
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    return jrender_response(template_name,
                              { 'form': form })

# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import base64
from inspect import getargspec
from math import ceil
from types import FunctionType
from urllib import quote
from urllib import urlencode

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.messages.api import get_messages
from django.core.urlresolvers import NoReverseMatch
from django.core.urlresolvers import RegexURLPattern
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.encoding import iri_to_uri

from settings import STATS_PERPAGE
from ugame.klasy.BaseGame import BaseGame
from ugame.models import UserProfile
from utils.eback.functions import return_json
from utils.eback.functions import sortfunc
from utils.eback.jsonwraper import dumps
from utils.eback.jsonwraper import loads
from utils.eback.threadlocal import set_user
from utils.jinja.fun_jinja import jrender

from ..generic.constants import MODULE_AUTH_SESSION_KEY

registry = []
urlpatterns = []


def url_wrapper(request, response_data, config, real_kwargs):
    from utils.jinja.filters import url
    """def url(*args, **kwargs):
        if 'kwargs' in kwargs:
            kw_tmp = kwargs["kwargs"]
            for k in kw_tmp:
                kwargs[k] = kw_tmp[k]
            del kwargs["kwargs"]
        viewname = args[0]
        url = reverse(viewname, kwargs=kwargs)

        return url
    """
    return url


def back_url_wrapper(request, config, kwargs):
    def url(name):
        back_url = None
        _back = {}
        if "_back" in request.REQUEST:
            _back = loads(base64.b64decode(request.REQUEST["_back"]))
            if name in _back:
                try:
                    back_url = reverse(_back[name]["urlname"], kwargs=_back[name]["kwargs"])
                except NoReverseMatch:
                    pass
        if not back_url:
            back_url = reverse(config.urlname, kwargs=kwargs)
        url = "%s?%s" % (
                       back_url,
                       urlencode({"_back": base64.b64encode(dumps(_back))})
                       )
        return iri_to_uri(url)
    return url


class Menu(object):
    main_menu = {
                 "zamowienia": {"name": "Zamówienia", "kolej": 1, "urls": []},
                 "produkty": {"name": "Produkty", "kolej": 2, "urls": []},
                 "imprezy": {"name": "Imprezy", "kolej": 3, "urls": []},
                 "artysci": {"name": "Artyści", "kolej": 4, "urls": []},
                 "zawartosc_strony": {"name": "Zawartość strony", "kolej": 5, "urls": []},
                 "ustawienia": {"name": "Ustawienia", "kolej": 6, "urls": []},
                 "narzedzia": {"name": "Narzędzia", "kolej": 7, "urls": []},
                 }
    menu = []

    def add_view(self, class_items, view, url):
        main_menu = getattr(view, "main_menu", None)
        if not main_menu:
            main_menu = class_items.get(view.__name__ + "_main_menu", None)
        if main_menu:
            main_menu["url"] = url
            self.main_menu[main_menu["menu"]]["urls"].append(main_menu)

    def finalize(self):
        for m in self.main_menu:
            self.main_menu[m]["urls"].sort(sortfunc)
            self.menu.append(self.main_menu[m])
        self.menu.sort(sortfunc)

    def get_menu(self):
        return self.menu

menu = Menu()


class Urls:
    pass


class Config:
    pass


class ModulesUrls:
    def get(self, module):
        return getattr(self, module)

    def add(self, module, site, url):
        if not hasattr(self, module):
            setattr(self, module, Urls())
        setattr(getattr(self, module), site, url)

urls = ModulesUrls()


def render_html(new_self, config, response_data,):
    if isinstance(response_data, dict):
        response_data["menu"] = menu.get_menu()
        response_data["this"] = new_self
        response_data["urls"] = urls
        response_data['request'] = new_self.request
        response_data['user'] = new_self.user
        response_data['user_messages'] = get_messages(new_self.request)
        if new_self.user and new_self.user.is_active:
            response_data["stats_page"] = int(ceil(float(UserProfile.objects.filter(points__gt=new_self.user.userprofile.points).count()) / STATS_PERPAGE))

        response_data["url"] = url_wrapper(new_self.request, response_data, config, new_self.kwargs)
        response_data["back_url"] = back_url_wrapper(new_self.request, config, new_self.kwargs)
        response_data["back_url"]("list")
        return jrender(new_self.request, config.template, response_data)
    else:
        return response_data


class CmsMetaclass(type):

    def __new__(cls, class_name, bases, attrs):

        module = attrs['__module__'].split(".", 2)[2].replace(".", "/")

        # attrs['__module__'].rsplit( ".", 1 )[-1]
        application = CmsMetaclass.__module__.split(".", 1)[0]

        cls = type.__new__(cls, class_name, bases, attrs)
        cls.application = application
        cls.module = module

        class_items = {}
        for parent in bases:
            class_items.update(parent.__dict__)
        class_items.update(attrs)

        for name, view in class_items.iteritems():
            if type(view) is not FunctionType:
                continue
            if name.startswith("site_"):
                name = name.replace("site_", "")

                config = Config()
                config.name = name

                template = getattr(view, "template", None)
                if not template:
                    template = "%s/%s.html" % (module, name)

                template = "%s/%s" % (application, template)

                config.template = template

                args, _, _, defaults = getargspec(view)
                defaults = defaults or []
                defaults_args = dict(zip(list(args[-len(defaults):]), defaults))
                args = getargspec(view).args
                args.remove("self")

                r = []
                if hasattr(view, "url"):
                    regex = getattr(view, "url")
                else:
                    regex = "{application}/{module}/{method}/{{r}}$".format(application=application,
                                                                            module=module, method=name)

                view_name = "{application}_{module}_{method}".format(application=application,
                                                                     module=module, method=name)
                config.urlname = view_name
                urls.add(module, name, view_name)
                callback = CmsMetaclass.get_view(cls, config, view.__name__)
                for a in args:
                    if a in defaults_args:
                        url = RegexURLPattern(regex=regex.format(r="".join(r)), callback=callback, name=view_name)
                        urlpatterns.append(url)
                    r.append("(?P<{name}>[-\w]+)/".format(name=a))

                if r:
                    url = RegexURLPattern(regex=regex.format(r="".join(r)), callback=callback, name=view_name)
                else:
                    url = RegexURLPattern(regex=regex.format(r="".join(r)), callback=callback, name=view_name)
                urlpatterns.append(url)
                menu.add_view(class_items, view, view_name)

        # fun = cls.get_view( "get_list", {"aa":"aa"} )
        cls.urls = getattr(urls, module)
        cls.all_urls = urls
        registry.append(cls)
        return cls

    def get_view(self, config, func):
        """
        Main entry point for a request-response process.
        """
        application = CmsMetaclass.__module__.split(".", 1)[0]

        def view(request, *args, **kwargs):
            application_user = None
            if MODULE_AUTH_SESSION_KEY in request.session:
                try:
                    application_user = User.objects.get(pk=request.session[MODULE_AUTH_SESSION_KEY])
                except:
                    pass

            new_self = self()
            setattr(request, application, application_user)
            request.user = application_user
            set_user(application_user)

            real_function = getattr(new_self, func)
            if not getattr(real_function, "without_user", False):
                if not application_user or not application_user.is_authenticated() or (not application_user.is_superuser and not application_user.is_staff):
                    return HttpResponseRedirect('%s?%s=%s' % (reverse(self.all_urls.user.login), REDIRECT_FIELD_NAME, quote(request.get_full_path())))

                if getattr(self, "superuser", False) and not application_user.is_superuser:
                    messages.info(self.request, message="Tylko administrator sklepu ma dostęp")
                    return HttpResponseRedirect(urls.main.main)

            new_self.user = application_user
            new_self.request = request
            new_self.args = args
            new_self.kwargs = kwargs
            new_self.url = config.urlname

            if application_user:
                new_self.game = BaseGame(new_self)
            else:
                new_self.game = None
            old_module_history = []
            if 'h' in request.session:
                if new_self.module in request.session['h']:
                    old_module_history = request.session['h'][new_self.module]

            result_type = getattr(real_function, "result_type", 'html')
            response_data = real_function(*args, **kwargs)
            if isinstance(response_data, dict):
                if 'site_name' in response_data:
                    this_url = getattr(new_self.urls, func.replace("site_", ""))
                    history_object = {"site_name": response_data["site_name"], "view": this_url, "kwargs": kwargs}
                    if history_object in old_module_history:
                        old_module_history = old_module_history[:old_module_history.index(history_object) + 1]
                    else:
                        old_module_history.append(history_object)
                request.session["h"] = {new_self.module: old_module_history}

            if new_self.game:
                new_self.game.save_all()

            if result_type == 'html':
                return render_html(new_self, config, response_data)
            elif result_type == 'json':
                return return_json(new_self, response_data)

            elif result_type == 'multi_json':
                ret_dict = {}
                for row in response_data:
                    type = row["type"]
                    name = row["name"]
                    data = row["data"]
                    if type == "html":
                        data = render_html(new_self, config, data).content

                    ret_dict[name] = data
                return return_json(new_self, ret_dict)

        return view

# -*- coding: utf-8 -*-
import traceback
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
from django.core.urlresolvers import get_callable
from jinja2 import FileSystemLoader, Environment, PackageLoader, ChoiceLoader, FileSystemBytecodeCache
from settings import URL
# from django.template import RequestContext


loader_array = []
for pth in getattr(settings, 'TEMPLATE_DIRS', ()):
    loader_array.append(FileSystemLoader(pth))

for app in settings.INSTALLED_APPS:
    loader_array.append(PackageLoader(app))

default_mimetype = getattr(settings, 'DEFAULT_CONTENT_TYPE')
global_exts = getattr(settings, 'JINJA_EXTS', ())

bcc = FileSystemBytecodeCache(settings.DIR_ROOT + '/tmp', 'sorema_%s.cache')
env = Environment(extensions=global_exts, loader=ChoiceLoader(loader_array), bytecode_cache=bcc)

global_imports = getattr(settings, 'JINJA_GLOBALS', ())
for imp in global_imports:
    method = get_callable(imp)
    method_name = getattr(method, 'jinja_name', None)
    if not method_name == None:
        env.globals[method_name] = method
    else:
        env.globals[method.__name__] = method

global_filters = getattr(settings, 'JINJA_FILTERS', ())
for imp in global_filters:
    method = get_callable(imp)
    method_name = getattr(method, 'jinja_name', None)
    if not method_name == None:
        env.filters[method_name] = method
    else:
        env.filters[method.__name__] = method

global_tests = getattr(settings, 'JINJA_TESTS', ())
for imp in global_tests:
    method = get_callable(imp)
    method_name = getattr(method, 'jinja_name', None)
    if not method_name == None:
        env.tests[method_name] = method
    else:
        env.tests[method.__name__] = method


def render_from_string(str_template, context={}):

    code = env.compile(str_template, name="asdas.html", filename="asdas.html")

    template = env.template_class.from_code(env, code, env.globals)
    print context
    return template.render(**context)


def render_to_string(filename, context={}):
    context["DOMAIN"] = URL
    context["settings"] = settings
    template = env.get_template(filename)
    rendered = template.render(**context)
    return rendered


def jrender_response(filename, context={}, mimetype=default_mimetype):
    try:
        rendered = render_to_string(filename, context)
        print datetime.now()
    except:
        print traceback.format_exc()
        raise
    return HttpResponse(rendered, mimetype=mimetype)


def jrender(request, filename, context={}, mimetype=default_mimetype):
    try:
        print datetime.now()
        rendered = render_to_string(filename, context)
        print datetime.now()
    except:
        print traceback.format_exc()
        raise
    return HttpResponse(rendered, mimetype=mimetype)

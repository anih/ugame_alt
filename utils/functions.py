# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import csv
import datetime
import json
import sys
from functools import wraps
from urllib import quote

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import logout
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from ugame.klasy.BaseGame import BaseGame
from ugame.models import Bany


def check_active(view_func):
    """
    Decorator for views that checks that the user passes the given test.

    Anonymous users will be redirected to login_url, while users that fail
    the test will be given a 403 error.
    """
    from django.conf import settings
    login_url = settings.LOGIN_URL

    def _checklogin(request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_active:
            bany = Bany.objects.filter(user=request.user, do__gte=datetime.datetime.now())
            if bany.count() > 0:
                # logout(request)
                return render_to_response("game/bany_info.html", {"bany": bany})
            request.GameObj = BaseGame(request)
            to_return = view_func(request, *args, **kwargs)
            request.GameObj.save_all()
            return to_return
        else:
            logout(request)

            return HttpResponseRedirect('%s?%s=%s' % (login_url, REDIRECT_FIELD_NAME, quote(request.get_full_path())))

    return wraps(view_func)(_checklogin)


def render_response(req, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)


def render_csv(dane):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=ranking.csv'

    writer = csv.writer(response)

    for wiersz in dane:
        writer.writerow(wiersz)

    return response


def json_view(func):
    def wrap(request, *a, **kw):
        response = None
        try:
            response = func(request, *a, **kw)
            assert isinstance(response, dict)
            if 'result' not in response:
                response['result'] = 'ok'
        except KeyboardInterrupt:
            # Allow keyboard interrupts through for debugging.
            raise
        except Exception, e:

            # Mail the admins with the error
            exc_info = sys.exc_info()
            subject = 'JSON view error: %s' % request.path
            try:
                request_repr = repr(request)
            except:
                request_repr = 'Request repr() unavailable'
            import traceback
            message = 'Traceback:\n%s\n\nRequest:\n%s' % (
                '\n'.join(traceback.format_exception(*exc_info)),
                request_repr,
            )

            # Come what may, we're returning JSON.
            if hasattr(e, 'message'):
                msg = e.message
            else:
                msg = 'Internal error' + ': ' + str(e)
            response = {'result': 'error',
                        'text': msg}
            raise

        json_string = json.dumps(response)
        return HttpResponse(json_string, mimetype='application/json')

    return wrap

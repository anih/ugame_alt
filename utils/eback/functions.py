# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.http import HttpResponse
from django.http import HttpResponseRedirect

from utils.eback.jsonwraper import dumps


def sortfunc(x, y):
    if 'kolej' not in x:
        x['kolej'] = 0
    if 'kolej' not in y:
        y['kolej'] = 0
    return cmp(x['kolej'], y['kolej'])


def return_json(new_self, response):
    try:
        if isinstance(response, HttpResponseRedirect):
            response = {"wynik": "ERROR_REDIRECT", "Location": response['location']}
        assert isinstance(response, (dict, list))
        if isinstance(response, dict) and 'result' not in response:
            response['result'] = 'ok'
    except KeyboardInterrupt:
        # Allow keyboard interrupts through for debugging.
        raise
    except Exception:
        raise

    json = dumps(response)
    resp = HttpResponse(json, content_type="application/json; charset=utf-8")

    return resp

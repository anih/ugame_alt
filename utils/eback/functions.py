# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from utils.eback.jsonwraper import dumps


def sortfunc(x, y):
    if 'kolej' not in x:
        x['kolej'] = 0
    if 'kolej' not in y:
        y['kolej'] = 0
    return cmp(x['kolej'], y['kolej'])


def return_json(new_self, response):
    try:
        if new_self.user and not new_self.user.is_anonymous():
            print "USER", new_self.user

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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()


def get_request():
    return getattr(_thread_locals, 'request', None)


def set_request(request):
    return setattr(_thread_locals, 'request', request)


def get_user():
    return getattr(_thread_locals, 'user', None)


def set_user(user):
    return setattr(_thread_locals, 'user', user)


class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        _thread_locals.request = request

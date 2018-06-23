from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser
from django.db import reset_queries

from ugame.models import IPAccess


class IPAccessMiddleware(object):
    def process_request(self, request):
        if not request.user == AnonymousUser():
            remoteip = request.META['REMOTE_ADDR']
            try:
                    if not IPAccess.objects.filter(ip=remoteip, user=request.user).count() > 0:
                        try:
                            ip_wewn = request.META['HTTP_FORWARD_X']
                            ip_wewn = ip_wewn.split(",")[0].strip()
                        except:
                            ip_wewn = None
                        IPAccess.objects.create(ip=remoteip, user=request.user, ip_wewn=ip_wewn)
            except IPAccess.DoesNotExist:
                pass
        return None

    def process_response(self, request, response):
        reset_queries()
        return response

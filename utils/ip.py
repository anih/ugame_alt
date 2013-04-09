from django.contrib.auth.models import AnonymousUser
from ugame.models import IPAccess
from django.db import reset_queries


class IPAccessMiddleware(object):
    def process_request(self, request):
        if not request.user == AnonymousUser():
            remoteip = request.META['REMOTE_ADDR']
            try:
                    if not IPAccess.objects.filter(ip=remoteip, user=request.user).count() > 0:
                        try:
                            print request.user.username
                            print request.META['HTTP_FORWARD_X']
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

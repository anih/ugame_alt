from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from main.models import Config
from utils.jinja.fun_jinja import jrender_response


def main(request):
    config = Config.objects.get(pk=1)
    if request.user.is_authenticated() and request.user.is_active:
        # return HttpResponseRedirect('/game')
        return jrender_response('main/frames.html', {'config': config})
    else:
        return jrender_response('main/index.html', {})


def regulamin(request):
    return jrender_response('regulamin.html', {})

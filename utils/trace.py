from __future__ import unicode_literals
from __future__ import division

import datetime
import traceback
from hashlib import md5

from django.db import connection, reset_queries
from django.http import Http404


class TraceMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return
        tb_text = traceback.format_exc()
        checksum = md5(tb_text).hexdigest()
        try:
            path = request.path
        except:
            path = ''

        print(u"---------------------------------------------------------------------------------")
        print(tb_text)
        print(u"---------------------------------------------------------------------------------")

        # filename = 'trace/%s_%s_%s.html' % (
        # path.replace("/", "-"), str(datetime.datetime.now()).replace(" ", "_"), checksum)
        # FILE = open(filename, "w")
        # FILE.write(tb_text)
        # FILE.write("\n")
        # for q in connection.queries:
        #     if q["sql"]:
        #         FILE.write(q["sql"] + "\n")
        # FILE.close()
        reset_queries()
        return

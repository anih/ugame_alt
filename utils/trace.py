from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import traceback
from hashlib import md5

from django.db import connection
from django.db import reset_queries
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

# -*- coding: utf-8 -*-
import decimal
import json
import datetime


class DjangoJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            return o.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return float(o)
        else:
            return super(DjangoJSONEncoder, self).default(o)


def dumps(objects):
    return json.dumps(objects, cls=DjangoJSONEncoder, separators=(",", ":"))


def loads(s):
    return json.loads(s, parse_float=decimal.Decimal)

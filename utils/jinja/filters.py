# -*- coding: utf-8 -*-
from math import floor, ceil
from django import template
from datetime import datetime
# from django.template import Library
import re
import os
from PIL import Image
from PIL import ImageFilter
from django.utils.encoding import force_unicode, iri_to_uri, force_text
from django.core.urlresolvers import reverse
from django.conf import settings
from kwotaslownie import kwotaslownie
from django.utils.html import _js_escapes
from django.db.models import Model
from django.template.defaultfilters import striptags
from ugame.models import Smiles
from django.utils.safestring import mark_safe


def emoticons(tekst):
    # podstawowe bbcode
    # tekst = escape(tekst)
    bbdata = []
    for tag in Smiles.objects.all():
        replace = '<img src="%s">' % (tag.img,)
        co = '%s' % (re.escape(tag.tag),)
        bbdata.append((co, replace))
    for bbset in bbdata:
        p = re.compile(bbset[0], re.DOTALL)
        tekst = p.sub(bbset[1], tekst)

    return tekst


def bbcodes(value):
    """
    Generates (X)HTML from string with BBCode "markup".
    By using the postmark lib from:
    @see: http://code.google.com/p/postmarkup/

    """
    try:
        from postmarkup import render_bbcode
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError, "Error in {% bbcode %} filter: The Python postmarkup library isn't installed."
        return force_unicode(value)
    else:
        try:
            ret = mark_safe(emoticons(render_bbcode(value)))
        except:
            ret = 'Błąd składni'
        return ret

def strip_bbcode(value):
    """
    Strips BBCode tags from a string
    By using the postmark lib from:
    @see: http://code.google.com/p/postmarkup/

    """
    try:
        from postmarkup import strip_bbcode
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError, "Error in {% bbcode %} filter: The Python postmarkup library isn't installed."
        return force_unicode(value)
    else:
        return mark_safe(strip_bbcode(value))


def pretty_floor(text):
    return int(floor(text))


def kk_resources(liczba):
    if (liczba / 1000 / 1000) > 1000:
        return str(number_format(liczba / 1000000)) + " kk"
    if liczba / 1000 > 1000:
        return str(number_format(liczba / 1000)) + " k"
    return str(number_format(liczba))


def slownie_kwota(value):
    return kwotaslownie(value, 1)


def number_format(num, places=2):
    """Format a number with grouped thousands and given decimal places"""
    if num is None:
        return "-"

    if num < 0:
        num = num * -1
        ujemna = 1
    else:
        ujemna = None
    places = max(0, places)
    # try:
    #    tmp = "%.*f" % (places, num)
    # except:
    #    return "ERROR "

    try:
        tmp = "%.*f" % (places, num)
    except:
        raise
        return "-"
    point = tmp.find(".")
    integer = (point == -1) and tmp or tmp[:point]

    decimal = ""
    if num != int(num):
        decimal = (point != -1) and tmp[point:] or ""
        decimal = decimal.replace(".", ",")

    count = 0
    formatted = []
    for i in range(len(integer), 0, -1):
        count += 1
        formatted.append(integer[i - 1])
        if count % 3 == 0 and i - 1:
            formatted.append(" ")

    integer = "".join(formatted[::-1])
    if ujemna:
        integer = "-" + integer
    return integer + decimal


def mult(value, arg):
    "Multiplies the arg and the value"
    return value * arg


def ceilh(val):
    return int(ceil(val))


def sub(value, arg):
    "Subtracts the arg from the value"
    return value - arg


def div(value, arg):
    "Divides the value by the arg"
    return value / arg


def pretty_time(seconds):
    day = int(seconds / (24 * 3600))
    hs = int(seconds / 3600 % 24)
    min = int(seconds / 60 % 60)
    seg = int(seconds / 1 % 60)
    time = ''
    if(day != 0):
        time += str(day) + ':'
        if(hs < 10):
            hs = "0" + str(hs)
    if(min < 10):
        min = "0" + str(min)
    time += str(hs) + ':'
    time += str(min) + ':'
    if(seg < 10):
        seg = "0" + str(seg)
    time += str(seg) + ''
    return time


def thumbnail(file, size='200x200'):
    # defining the size
    if not file:
        return None
    spl = size.split('x')
    if len(spl) >= 2:
        x, y = [int(x) for x in spl]
    else:
        x = int(spl[0])
        y = 0
    # defining the filename and the miniature filename
    file_name = str(file)
    basename, format = file_name.rsplit('.', 1)
    miniature = basename + '_' + size + '.' + format

    miniature_filename = os.path.join(settings.MEDIA_ROOT, miniature)
    miniature_url = os.path.join(miniature)
    # if the image wasn't already resized, resize it
    if not os.path.exists(miniature_filename) or os.path.getmtime(miniature_filename) <= os.path.getmtime(os.path.join(settings.MEDIA_ROOT, file_name)):
        print '>>> debug: resizing the image to the format %s!' % size
        filename = os.path.join(settings.MEDIA_ROOT, file_name)
        if not os.path.exists(filename):
            return None
        image = Image.open(filename)
        size = image.size
        if not y > 0:
            print "y nie podano"
            y = x * size[1] / size[0]
        image.thumbnail((x, y), Image.ANTIALIAS)  # generate a 200x200 thumbnail
        try:
            image.filter(ImageFilter.SHARPEN)
        except:
            pass
        image.save(miniature_filename, image.format, quality=85)
    return miniature_url


def make_int(value):
    try:
        return int(floor(value))
    except:
        return 0


def tabularize(value, cols):
        """modifies a list to become a list of lists
        eg [1,2,3,4] becomes [[1,2], [3,4]] with an argument of 2"""
        try:
                cols = int(cols)
        except ValueError:
                return [value]
        return map(*([None] + [value[i::cols] for i in range(0, cols)]))


def intcomma(value):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', orig)
    if orig == new:
        return new
    else:
        return intcomma(new)


def url(*args, **kwargs):

    new_kwargs = {}

    if isinstance(args[0], dict):
        new_kwargs.update(args[0]["kwargs"])
        viewname = args[0]['url']
    else:
        viewname = args[0]

    if 'kwargs' in kwargs:
        kw_tmp = kwargs["kwargs"]
        for k in kw_tmp:
            kwargs[k] = kw_tmp[k]
        del kwargs["kwargs"]

    for k, v in kwargs.iteritems():
        if issubclass(v.__class__, Model):
            kwargs[k] = v.id

    new_kwargs.update(kwargs)

    return iri_to_uri(reverse(viewname, kwargs=new_kwargs))


def url_full(*args, **kwargs):
    return iri_to_uri(settings.DOMAIN + url(*args, **kwargs))


def now(arg=None):
    """Formats a date according to the given format."""
    from django.utils.dateformat import format
    if arg is None:
        arg = settings.DATE_FORMAT
    return format(datetime.now(), arg)


def date(value, arg=None):
    """Formats a date according to the given format."""
    from django.utils.dateformat import format
    if not value:
        return u''
    if arg is None:
        arg = settings.DATE_FORMAT
    return format(value, arg)


def escapejs(value):
    return mark_safe(force_text(value).translate(_js_escapes))


def floatformat(value, arg= -1):  # @IgnorePep8
    from django.template.defaultfilters import floatformat
    return floatformat(value, arg)


def linebreaks(value):
    from django.template.defaultfilters import linebreaks
    return linebreaks(value)


def truncate(s, length=255, killwords=True, end='...'):
    s = unicode(s)
    if len(s) <= length:
        return s
    elif killwords:
        return s[:length - len(end)] + end
    words = s.split(' ')
    result = []
    m = 0
    for word in words:
        m += len(word) + 1
        if m > length:
            break
        result.append(word)
    result.append(end)
    return u' '.join(result)


def striphtml(s):
    return striptags(s)


def split(s):
    return re.findall(r'\w+', s, re.UNICODE)

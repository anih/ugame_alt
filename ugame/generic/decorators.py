# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import wraps


def html_site( method, *args, **kwargs ):
    @wraps( method )
    def wrapper( self, *args, **kwargs ):
        res = method( self, *args, **kwargs )        
        return res
    return wrapper

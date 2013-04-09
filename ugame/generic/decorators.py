# -*- coding: utf-8 -*-
from functools import wraps
def html_site( method, *args, **kwargs ):
    @wraps( method )
    def wrapper( self, *args, **kwargs ):
        res = method( self, *args, **kwargs )        
        return res
    return wrapper


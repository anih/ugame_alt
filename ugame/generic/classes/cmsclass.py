# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class CMSClass( object ):

    def set_variable( self, key, value ):
        self.request.session[key] = value
    def get_variable( self, key ):
        return self.request.session.get( key, None )

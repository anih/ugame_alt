# -*- coding: utf-8 -*-

class CMSClass( object ):

    def set_variable( self, key, value ):
        self.request.session[key] = value
    def get_variable( self, key ):
        return self.request.session.get( key, None )

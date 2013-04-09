# -*- coding: utf-8 -*-
import inspect
from cms.generic.functions import sortfunc

class CMSMenuClass( object ):
    """
    @DynamicAttrs
    """
    topmenu_template = "generic/topmenu.html"
    leftmenu_template = "generic/leftmenu.html"

    def __init__( self ):
        if hasattr( self, "get_topmenu" ):
            self.get_topmenu()
        if hasattr( self, "get_leftmenu" ):
            self.get_leftmenu()

    def get_topmenu( self ):
        if not hasattr( self, "topmenu" ) or not self.topmenu:
            self.topmenu = []
        for name in dir( self ):
            item = getattr( self, name )
            if inspect.ismethod( item ):
                data = getattr( item, "topmenu" , None )
                if not data:
                    data = getattr( self, item.__name__ + "_topmenu" , None )
                if data:
                    data["url"] = getattr( self.urls, name.replace( "site_", "" ) )
                    self.topmenu.append( data )
        self.topmenu.sort( cmp = sortfunc )

    def get_leftmenu( self ):
        self.leftmenu = []
        for name in dir( self ):
            item = getattr( self, name )
            if inspect.ismethod( item ):
                data = getattr( item, "leftmenu" , None )
                if not data:
                    data = getattr( self, item.__name__ + "_leftmenu" , None )
                if data:
                    data["url"] = getattr( self.urls, name.replace( "site_", "" ) )
                    self.leftmenu.append( data )
        self.leftmenu.sort( cmp = sortfunc )


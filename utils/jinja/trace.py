import traceback
import datetime
from hashlib import md5 #@UnresolvedImport
from django.http import Http404

from django.db import connection

class TraceMiddleware( object ):
    def process_exception( self, request, exception ):
        if isinstance( exception, Http404 ):
            return
        tb_text = traceback.format_exc()
        checksum = md5( tb_text ).hexdigest()
        try:
            path = request.path
        except:
            path = ''
        filename = 'trace/%s_%s_%s.html' % ( path.replace( "/", "-" ), str( datetime.datetime.now() ).replace( " ", "_" ), checksum )
        FILE = open( filename, "w" )
        FILE.write( tb_text )
        FILE.write( "\n" )
        for q in connection.queries: #@UndefinedVariable
            if q["sql"]:
                FILE.write( q["sql"] + "\n" )
        FILE.close()
        
        return 

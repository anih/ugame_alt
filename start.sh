nice -n 19 su ugame -c 'python ./manage.py runfcgi --settings=web.settings maxchildren=15 maxspare=15 minspare=12 method=prefork pidfile=/home/ugame/django.pid  umask=027 daemonize=false maxrequests=5 -v 2 socket=/home/ugame/ugame.sock '
#outlog=/home/ugame/web/stdout.log errlog=/home/ugame/web/stderr.log >> /home/ugame/web/std.log

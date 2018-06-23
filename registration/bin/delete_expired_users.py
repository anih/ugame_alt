"""
A script which removes expired/inactive user accounts from the
database.

This is intended to be run as a cron job; for example, to have it run
at midnight each Sunday, you could add lines like the following to
your crontab::

    DJANGO_SETTINGS_MODULE=yoursite.settings
    0 0 * * sun python /path/to/registration/bin/delete_expired_users.py

See the method ``delete_expired_users`` of the ``RegistrationManager``
class in ``registration/models.py`` for further documentation.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

if __name__ == '__main__':
    from registration.models import RegistrationProfile
    RegistrationProfile.objects.delete_expired_users()

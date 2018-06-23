# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.messages import INFO, constants
from django.contrib.messages.storage.base import BaseStorage, LEVEL_TAGS
from django.db import models
from django.utils.encoding import force_text

from ugame.models import APP_LABEL


class Message(models.Model):
    class Meta:
        app_label = 'ugame'
        ordering = ('id', )

    user = models.ForeignKey(User, null=True, blank=True)
    level = models.IntegerField()
    message = models.TextField()
    extra_tags = models.TextField()

    def _get_tags(self):
        label_tag = force_text(LEVEL_TAGS.get(self.level, ''),
                               strings_only=True)
        extra_tags = force_text(self.extra_tags, strings_only=True)
        if extra_tags and label_tag:
            return ' '.join([extra_tags, label_tag])
        elif extra_tags:
            return extra_tags
        elif label_tag:
            return label_tag
        return ''

    tags = property(_get_tags)


class DBStorage(BaseStorage):
    """
    Stores messages in the session (that is, django.contrib.sessions).
    """

    def _get(self, *args, **kwargs):
        """
        Retrieves a list of messages from the request's session.  This storage
        always stores everything it is given, so return True for the
        all_retrieved flag.
        """
        return Message.objects.filter(user=self.request.user), True

    def _store(self, messages, response, *args, **kwargs):
        """
        Stores a list of messages to the request's session.
        """
        Message.objects.filter(user=self.request.user).delete()
        if messages:
            for message in messages:
                Message.objects.create(
                    user=self.request.user,
                    level=message.level or INFO,
                    message=message.message,
                    extra_tags=message.extra_tags,
                )
        return []


def send_info_message(user, message, extra_tags=''):
    Message.objects.create(
        user=user,
        level=constants.INFO,
        message=message,
        extra_tags=extra_tags,
    )


def send_error_message(user, message, extra_tags=''):
    Message.objects.create(
        user=user,
        level=constants.ERROR,
        message=message,
        extra_tags=extra_tags,
    )


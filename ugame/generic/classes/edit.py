# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect


class CMSEditClass(object):

    fields = None
    exclude = None
    return_url = "list"

    def site_list(self):
        object_list = self.model.objects.all()
        return {"object_list":object_list, "site_name":self.name}  # , "_start_back":True}

    def _get_form(self):
        class TheForm(ModelForm):
            class Meta:
                fields = self.fields
                exclude = self.exclude
                model = self.model
        self.form_class = TheForm

    def site_edit(self , object_id=None):
        self._get_form()
        if object_id:
            instance = self.model.objects.get(pk=object_id)
        else:
            instance = self.model()
        form = self.form_class(instance=instance)
        if self.request.method == 'POST':
            form = self.form_class(data=self.request.REQUEST, files=self.request.FILES, instance=instance)
            if form.is_valid():
                instance = form.save()
                messages.info(self.request, message="Dane zostały zapisane")
                return HttpResponseRedirect(reverse(getattr(self.urls, self.return_url)))
        return {"form":form, "instance":instance, "site_name":self.name,
                "submenu":"edit"}


    def site_delete(self , object_id):
        try:
            instance = self.model.objects.get(pk=object_id)
        except self.model.DoesNotExist:
            pass
        finally:
            instance.delete()
            messages.info(self.request, message="Dane zostały usunięte")
        return HttpResponseRedirect(reverse(self.urls.list))

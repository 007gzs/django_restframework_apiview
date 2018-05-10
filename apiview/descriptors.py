# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor, ForwardOneToOneDescriptor

from apiview import model


class ForwardManyToOneCacheDescriptor(ForwardManyToOneDescriptor):
    def get_cache_object(self, instance):
        remote_model = self.field.remote_field.model
        if not issubclass(remote_model, model.BaseModel) or not remote_model._MODEL_WITH_CACHE:
            return None
        if len(self.field.foreign_related_fields) != 1:
            return None

        val = self.field.get_local_related_value(instance)
        if len(val) != 1:
            return None
        return remote_model.get_obj_by_unique_key_from_cache(**self.field.get_filter_kwargs_for_object(instance))

    def get_object(self, instance):
        try:
            ret = self.get_cache_object(instance)
        except Exception:
            ret = None
        if ret is not None:
            return ret
        return super(ForwardManyToOneCacheDescriptor, self).get_object(instance)


class ForwardOneToOneCacheDescriptor(ForwardOneToOneDescriptor, ForwardManyToOneCacheDescriptor):
    pass

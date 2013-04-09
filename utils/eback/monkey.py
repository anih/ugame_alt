# -*- coding: utf-8 -*-
import importlib


def CASCADE_NEW(collector, field, sub_objs, using):
    from django.db.models.deletion import ProtectedError
    raise ProtectedError("Cannot delete some instances of model '%s' because "
        "they are referenced through a protected foreign key: '%s.%s'" % (
            field.rel.to.__name__, sub_objs[0].__class__.__name__, field.name
        ),
        sub_objs
    )

#module = __import__("django.db.models.deletion")
module = importlib.import_module("django.db.models.deletion")
collect_orig = module.Collector.collect


def collect_new(self, objs, source=None, nullable=False, collect_related=True,
        source_attr=None, reverse_dependency=False):
    """
    Adds 'objs' to the collection of objects to be deleted as well as all
    parent instances.  'objs' must be a homogenous iterable collection of
    model instances (e.g. a QuerySet).  If 'collect_related' is True,
    related objects will be handled by their respective on_delete handler.

    If the call is the result of a cascade, 'source' should be the model
    that caused it and 'nullable' should be set to True, if the relation
    can be null.

    If 'reverse_dependency' is True, 'source' will be deleted before the
    current model, rather than after. (Needed for cascading to parent
    models, the one case in which the cascade follows the forwards
    direction of an FK rather than the reverse direction.)
    """
    new_objs = self.add(objs, source, nullable,
                        reverse_dependency=reverse_dependency)
    if not new_objs:
        return

    model = new_objs[0].__class__

    # Recursively collect parent models, but not their related objects.
    # These will be found by meta.get_all_related_objects()
    for parent_model, ptr in model._meta.parents.iteritems():
        if ptr:
            parent_objs = [getattr(obj, ptr.name) for obj in new_objs]
            self.collect(parent_objs, source=model,
                         source_attr=ptr.rel.related_name,
                         collect_related=False,
                         reverse_dependency=True)

    if collect_related:
        for related in model._meta.get_all_related_objects(
                include_hidden=True, include_proxy_eq=True):
            field = related.field
            if related.model._meta.auto_created:
                self.add_batch(related.model, field, new_objs)
            else:
                sub_objs = self.related_objects(related, new_objs)
                if not sub_objs:
                    continue

                if field.rel.on_delete == module.CASCADE:
                    field.rel.on_delete = CASCADE_NEW

                field.rel.on_delete(self, field, sub_objs, self.using)

        # TODO This entire block is only needed as a special case to
        # support cascade-deletes for GenericRelation. It should be
        # removed/fixed when the ORM gains a proper abstraction for virtual
        # or composite fields, and GFKs are reworked to fit into that.
        for relation in model._meta.many_to_many:
            if not relation.rel.through:
                sub_objs = relation.bulk_related_objects(new_objs, self.using)
                self.collect(sub_objs,
                             source=model,
                             source_attr=relation.rel.related_name,
                         nullable=True)

module.Collector.collect = collect_new

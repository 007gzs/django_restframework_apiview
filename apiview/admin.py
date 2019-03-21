# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from django.db.models import FieldDoesNotExist
try:
    from django.db.models.related import RelatedObject
except ImportError:
    from django.db.models.fields.reverse_related import ForeignObjectRel as RelatedObject
from django.forms import widgets
from django.utils import six
from django.contrib import admin
from django.templatetags.static import static
from django.db.models.constants import LOOKUP_SEP
from django.db.models.sql.constants import QUERY_TERMS

from apiview import admintools
from apiview import model


class BaseAdmin(admintools.ProxyModelAdmin):

    class Media:
        js = (static('apiview/js/filter.js'),)
        css = {
            'all': (static('apiview/css/filter.css'),),
        }

    def lookup_allowed(self, lookup, value):
        '''
        To fix IncorrectLookupParameters Error in django less than 1.8
        '''
        m = self.model
        # Check FKey lookups that are allowed, so that popups produced by
        # ForeignKeyRawIdWidget, on the basis of ForeignKey.limit_choices_to,
        # are allowed to work.
        for l in m._meta.related_fkey_lookups:
            for k, v in widgets.url_params_from_lookup_dict(l).items():
                if k == lookup and v == value:
                    return True

        parts = lookup.split(LOOKUP_SEP)

        # Last term in lookup is a query term (__exact, __startswith etc)
        # This term can be ignored.
        if len(parts) > 1 and parts[-1] in QUERY_TERMS:
            parts.pop()

        # Special case -- foo__id__exact and foo__id queries are implied
        # if foo has been specifically included in the lookup list; so
        # drop __id if it is the last part. However, first we need to find
        # the pk attribute name.
        rel_name = None
        for part in parts[:-1]:
            try:
                field = m._meta.get_field(part)
            except FieldDoesNotExist:
                # Lookups on non-existent fields are ok, since they're ignored
                # later.
                return True
            if hasattr(field, 'rel'):
                if field.rel is None:
                    # This property or relation doesn't exist, but it's allowed
                    # since it's ignored in ChangeList.get_filters().
                    return True
                m = field.rel.to
                rel_name = field.rel.get_related_field().name
            elif isinstance(field, RelatedObject):
                m = field.model
                rel_name = m._meta.pk.name
            else:
                rel_name = None
        if rel_name and len(parts) > 1 and parts[-1] == rel_name:
            parts.pop()

        if len(parts) == 1:
            return True
        clean_lookup = LOOKUP_SEP.join(parts)
        for item in self.list_filter:
            if isinstance(item, six.string_types):
                if clean_lookup == item:
                    return True
            elif isinstance(item, (tuple, list)):
                if clean_lookup == item[0]:
                    return True

        return clean_lookup == self.date_hierarchy


def site_register(model_or_iterable, admin_class=None, site=None, **options):
    if site is None:
        site = admin.site
    if admin_class is None:
        admin_class = BaseAdmin
    if not isinstance(model_or_iterable, (list, set, tuple)):
        model_or_iterable = [model_or_iterable]
    for m in model_or_iterable:
        if issubclass(m, model.BaseModel):
            m2m_fields = []
            search_fields = list(m.search_fields())
            generic_foreign_keys = []
            generic_relations = []
            list_display = []

            for key, field in m._meta._forward_fields_map.items():
                if key != field.name:
                    continue
                if field.is_relation:
                    if field.one_to_many:
                        generic_relations.append(field.name)
                    elif field.many_to_many:
                        m2m_fields.append(field.name)
                    elif field.many_to_one and hasattr(field.remote_field, 'model') and field.remote_field.model:
                        generic_foreign_keys.append(field.name)
                    elif field.one_to_one and hasattr(field.remote_field, 'model') and field.remote_field.model:
                        generic_foreign_keys.append(field.name)

            filter_horizontal = m2m_fields
            raw_id_fields = generic_foreign_keys
            if admin_class is not None and admin_class != BaseAdmin:
                _list_display = admin_class.list_display
                if _list_display is None:
                    list_display = ()
                elif len(_list_display) > 0:
                    list_display = _list_display
                _search_fields = admin_class.search_fields
                if _search_fields is None:
                    search_fields = ()
                elif len(_search_fields) > 0:
                    search_fields = _search_fields
                _raw_id_fields = admin_class.raw_id_fields
                if _raw_id_fields is None:
                    raw_id_fields = ()
                elif len(_raw_id_fields) > 0:
                    raw_id_fields = _raw_id_fields
                _filter_horizontal = admin_class.filter_horizontal
                if _filter_horizontal is None:
                    filter_horizontal = ()
                elif len(_filter_horizontal) > 0:
                    filter_horizontal = _filter_horizontal

            if len(search_fields) > 0:
                if 'search_fields' not in options:
                    options['search_fields'] = search_fields
            if len(raw_id_fields) > 0:
                if 'raw_id_fields' not in options:
                    options['raw_id_fields'] = raw_id_fields
            if len(filter_horizontal) > 0:
                if 'filter_horizontal' not in options:
                    options['filter_horizontal'] = filter_horizontal

            if 'list_display' in options:
                list_display = list(list_display) + list(options['list_display'])

            if len(list_display) > 0:
                for attr in list_display:
                    if '__' in attr and not attr.startswith('_'):
                        _boolean, _short_description = m.get_child_field(attr)
                        key = '{}_boolean'.format(attr)
                        if not hasattr(admin_class, key) and key not in options:
                            options[key] = _boolean
                        key = '{}_short_description'.format(attr)
                        if not hasattr(admin_class, key) and key not in options:
                            options[key] = _short_description

            autocomplete_lookup_fields = options.get('autocomplete_lookup_fields',
                                                     getattr(admin_class, 'autocomplete_lookup_fields', {}))
            if 'raw_id_fields' in options and 'fk' not in autocomplete_lookup_fields:
                autocomplete_lookup_fields['fk'] = options['raw_id_fields']
            # if len(m2m_fields) > 0 and 'm2m' not in autocomplete_lookup_fields:
            #     autocomplete_lookup_fields['m2m'] = m2m_fields
            options['autocomplete_lookup_fields'] = autocomplete_lookup_fields

        site.register(m, admin_class, **options)

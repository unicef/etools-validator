from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Model, ObjectDoesNotExist
from django.db.models.fields.files import FieldFile
from itertools import chain


def get_all_field_names(model):
    '''Return a list of all field names that are possible for
    this model (including reverse relation names).
    Any internal-only field names are not included.

    Replacement for MyModel._meta.get_all_field_names()
    which does not exist under Django 1.10.
    https://github.com/django/django/blob/stable/1.7.x/django/db/models/options.py#L422
    https://docs.djangoproject.com/en/1.10/ref/models/meta/#migrating-from-the-old-api
    '''
    return list(set(chain.from_iterable(
        (field.name, field.attname) if hasattr(field, 'attname') else (field.name, )
        for field in model._meta.get_fields()
        if not (field.many_to_one and field.related_model is None) and not isinstance(field, GenericForeignKey)
    )))


def check_editable_fields(obj, fields):
    if not getattr(obj, 'old_instance', None):
        return False, fields
    for field in fields:
        old_instance = obj.old_instance
        if getattr(obj, field) != getattr(old_instance, field):
            return False, field
    return True, None


def check_required_fields(obj, fields):
    error_fields = []
    for f_name in fields:
        try:
            field = getattr(obj, f_name)
        except ObjectDoesNotExist:
            return False, f_name
        try:
            response = field.filter().count() > 0
        except AttributeError:
            if isinstance(field, FieldFile):
                response = getattr(field, 'name', None) or False
            else:
                response = field is not None
        if response is False:
            error_fields.append(f_name)

    if error_fields:
        return False, error_fields
    return True, None


def field_comparison(f1, f2):
    if isinstance(f1, FieldFile):
        new_file = getattr(f1, 'name', None)
        old_file = getattr(f2, 'name', None)
        if new_file != old_file:
            return False
    elif f1 != f2:
        return False
    return True


def check_rigid_model_instance(old_obj, new_obj):
    if not isinstance(old_obj, Model) or not isinstance(new_obj, Model):
        # one of instances can be None, in this case we don't need to check all fields
        return old_obj == new_obj

    field_names = get_all_field_names(old_obj)

    for field in field_names:
        try:
            new_value = getattr(old_obj, field, None)
        except ObjectDoesNotExist:
            new_value = None
        try:
            old_value = getattr(new_obj, field, None)
        except ObjectDoesNotExist:
            old_value = None
        if not field_comparison(new_value, old_value):
            return False

        # there is no check for instance class so we don't go deeper than 1 level

    return True


def check_rigid_related(obj, related):
    current_related = list(getattr(obj, related).filter())
    old_related = getattr(obj.old_instance, '{}_old'.format(related), None)
    if old_related is None:
        # if old related was not set as an attribute on the object, assuming no changes
        return True
    if len(current_related) != len(old_related):
        return False
    if len(current_related) == 0:
        return True

    current_related.sort(key=lambda x: x.id)
    old_related.sort(key=lambda x: x.id)
    comparison_map = zip(current_related, old_related)
    # check if any field on the related model was changed
    for old_obj, new_obj in comparison_map:
        if not check_rigid_model_instance(old_obj, new_obj):
            return False
    return True


def check_rigid_fields(obj, fields, old_instance=None, related=False):
    if not old_instance and not getattr(obj, 'old_instance', None):
        # since no old version of the object was passed in, we assume there were no changes
        return True, None
    for f_name in fields:
        old_instance = old_instance or obj.old_instance
        try:
            new_field = getattr(obj, f_name, None)
        except ObjectDoesNotExist:
            new_field = None
        try:
            old_field = getattr(old_instance, f_name, None)
        except ObjectDoesNotExist:
            # in case it's OneToOne related field
            old_field = None
        if hasattr(new_field, 'all'):
            # this could be a related field, unfortunately i can't figure out a isinstance check
            if related:
                if not check_rigid_related(obj, f_name):
                    return False, f_name

        elif isinstance(old_field, Model) or isinstance(new_field, Model):
            if not check_rigid_model_instance(old_field, new_field):
                return False, f_name

        elif not field_comparison(new_field, old_field):
            return False, f_name

    return True, None


def update_object(obj, kwdict):
    for k, v in kwdict.items():
        if isinstance(v, list):
            getattr(obj, k).set(v)
        else:
            setattr(obj, k, v)

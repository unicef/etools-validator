from django.db.models import ObjectDoesNotExist

from rest_framework.exceptions import ValidationError

from validator.parsers import parse_multipart_data


class ValidatorViewMixin(object):
    def _parse_data(self, request):
        dt_cp = request.data
        for k in dt_cp:
            if dt_cp[k] == 'null':
                dt_cp[k] = None
            elif dt_cp[k] == 'true':
                dt_cp[k] = True
            elif dt_cp[k] == 'false':
                dt_cp[k] = False

        dt = parse_multipart_data(dt_cp)
        return dt

    def up_related_field(
            self,
            mother_obj,
            field,
            fieldClass,
            fieldSerializer,
            rel_prop_name,
            reverse_name,
            partial=False,
            nested_related_names=None
    ):
        if not field:
            return

        if isinstance(field, list):
            for item in field:
                item.update({reverse_name: mother_obj.pk})
                nested_related_data = {}
                if nested_related_names:
                    nested_related_data = {k: v for k, v in item.items()
                                           if k in nested_related_names}
                if item.get('id', None):
                    try:
                        instance = fieldClass.objects.get(id=item['id'])
                    except fieldClass.DoesNotExist:
                        instance = None

                    instance_serializer = fieldSerializer(
                        instance=instance,
                        data=item,
                        partial=partial,
                        context=nested_related_data
                    )
                else:
                    instance_serializer = fieldSerializer(
                        data=item,
                        context=nested_related_data
                    )

                try:
                    instance_serializer.is_valid(raise_exception=True)
                    # ValidationError can be raised by one of the sub-related
                    # fields inside the serializer on save
                    instance_serializer.save()
                except ValidationError as e:
                    e.detail = {rel_prop_name: e.detail}
                    raise e
        else:
            # This is in case we have a OneToOne field
            field.update({reverse_name: mother_obj.pk})
            nested_related_data = {}
            if nested_related_names:
                nested_related_data = {k: v for k, v in field.items()
                                       if k in nested_related_names}
            if field.get('id', None):
                try:
                    instance = fieldClass.objects.get(id=field['id'])
                except fieldClass.DoesNotExist:
                    instance = None

                instance_serializer = fieldSerializer(
                    instance=instance,
                    data=field,
                    partial=partial,
                    context=nested_related_data
                )
            else:
                instance_serializer = fieldSerializer(
                    data=field,
                    context=nested_related_data
                )

            try:
                instance_serializer.is_valid(raise_exception=True)
                # ValidationError can be raised by one of the sub-related
                # fields inside the serializer on save
                instance_serializer.save()
            except ValidationError as e:
                e.detail = {rel_prop_name: e.detail}
                raise e

    @staticmethod
    def _get_model_for_field(obj, field):
        return obj.__class__._meta.get_field(field).related_model

    @staticmethod
    def _get_reverse_for_field(obj, field):
        return obj.__class__._meta.get_field(field).remote_field.name

    def my_create(
            self,
            request,
            related_f,
            nested_related_names=None,
            **kwargs
    ):
        my_relations = {}
        partial = kwargs.pop('partial', False)
        data = self._parse_data(request)

        for f in related_f:
            my_relations[f] = data.pop(f, [])

        main_serializer = self.get_serializer(data=data)
        main_serializer.context['skip_global_validator'] = True
        main_serializer.is_valid(raise_exception=True)

        main_object = main_serializer.save()

        for k, v in my_relations.items():
            self.up_related_field(
                main_object,
                v,
                self._get_model_for_field(main_object, k),
                self.SERIALIZER_MAP[k],
                k,
                self._get_reverse_for_field(main_object, k),
                partial,
                nested_related_names
            )

        return main_serializer

    def my_update(
            self,
            request,
            related_f,
            nested_related_names=None,
            **kwargs
    ):
        partial = kwargs.pop('partial', False)
        data = self._parse_data(request)

        my_relations = {}
        for f in related_f:
            my_relations[f] = data.pop(f, [])

        old_instance = self.get_object()
        instance = self.get_object()
        main_serializer = self.get_serializer(
            instance,
            data=data,
            partial=partial
        )
        main_serializer.context['skip_global_validator'] = True
        main_serializer.is_valid(raise_exception=True)

        main_object = main_serializer.save()

        for k in my_relations.keys():
            try:
                rel_field_val = getattr(old_instance, k)
            except ObjectDoesNotExist:
                pass
            else:
                prop = '{}_old'.format(k)

                try:
                    val = list(rel_field_val.all())
                except AttributeError:
                    # This means OneToOne field
                    val = rel_field_val

                setattr(old_instance, prop, val)

        for k, v in my_relations.items():
            self.up_related_field(
                main_object,
                v,
                self._get_model_for_field(main_object, k),
                self.SERIALIZER_MAP[k],
                k,
                self._get_reverse_for_field(main_object, k),
                partial,
                nested_related_names
            )

        return self.get_object(), old_instance, main_serializer

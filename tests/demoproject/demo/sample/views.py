from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from etools_validator.mixins import ValidatorViewMixin

from .models import DemoModel
from .serializers import DemoChildModelSerializer, DemoModelSerializer, SpecialModelSerializer
from .validations import DemoModelValidation


class DemoCreateView(ValidatorViewMixin, CreateAPIView):
    serializer_class = DemoModelSerializer

    SERIALIZER_MAP = {
        "children": DemoChildModelSerializer
    }

    def create(self, request, *args, **kwargs):
        related_fields = ['children']
        serializer = self.my_create(request, related_fields, **kwargs)
        instance = serializer.instance

        validator = DemoModelValidation(instance, user=request.user)
        if not validator.is_valid:
            raise ValidationError({'errors': validator.errors})

        headers = self.get_success_headers(serializer.data)

        data = DemoModelSerializer(
            instance,
            context=self.get_serializer_context()
        ).data
        return Response(
            data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class DemoUpdateView(ValidatorViewMixin, UpdateAPIView):
    queryset = DemoModel.objects.all()
    serializer_class = DemoModelSerializer
    validation_class = DemoModelValidation

    SERIALIZER_MAP = {
        "children": DemoChildModelSerializer,
        "special": SpecialModelSerializer,
    }

    def get_validation_class(self):
        return self.validation_class

    def update(self, request, *args, **kwargs):
        related_fields = ['children', 'special']
        instance, old_instance, serializer = self.my_update(
            request,
            related_fields,
            **kwargs
        )

        validator = self.get_validation_class()(
            instance,
            old=old_instance,
            user=request.user
        )

        if not validator.is_valid:
            raise ValidationError(validator.errors)

        return Response(
            DemoModelSerializer(
                instance,
                context=self.get_serializer_context()
            ).data
        )


class DemoUpdateNonSerializedView(ValidatorViewMixin, UpdateAPIView):
    queryset = DemoModel.objects.all()
    serializer_class = DemoModelSerializer

    def update(self, request, *args, **kwargs):
        related_fields = []
        related_non_serialized_fields = ['others']
        instance, old_instance, serializer = self.my_update(
            request,
            related_fields,
            related_non_serialized_fields=related_non_serialized_fields,
            **kwargs
        )

        validator = DemoModelValidation(
            instance,
            old=old_instance,
            user=request.user
        )

        if not validator.is_valid:
            raise ValidationError(validator.errors)

        return Response(
            DemoModelSerializer(
                instance,
                context=self.get_serializer_context()
            ).data
        )

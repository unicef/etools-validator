from rest_framework import serializers

from .models import DemoChildModel, DemoModel


class DemoChildModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoChildModel
        fields = "__all__"


class DemoModelSerializer(serializers.ModelSerializer):
    children = DemoChildModelSerializer(many=True, read_only=True)

    class Meta:
        model = DemoModel
        fields = "__all__"

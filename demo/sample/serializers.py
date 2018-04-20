from rest_framework import serializers

from demo.sample.models import DemoModel, DemoChildModel


class DemoChildModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoChildModel
        fields = ("name", )


class DemoModelSerializer(serializers.ModelSerializer):
    children = DemoChildModelSerializer(many=True, read_only=True)

    class Meta:
        model = DemoModel
        fields = "__all__"

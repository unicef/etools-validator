import factory

from demo.sample import models


class DemoModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DemoModel

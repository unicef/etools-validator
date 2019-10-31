import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from factory import fuzzy

from demo.sample import models


class DemoModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DemoModel


class DemoChildModelFactory(factory.django.DjangoModelFactory):
    parent = factory.SubFactory(DemoModelFactory)

    class Meta:
        model = models.DemoChildModel


class SpecialModelFactory(factory.django.DjangoModelFactory):
    demo = factory.SubFactory(DemoModelFactory)

    class Meta:
        model = models.SpecialModel


class ManyModelFactory(factory.django.DjangoModelFactory):
    name = fuzzy.FuzzyText(length=50)

    class Meta:
        model = models.ManyModel


class UserFactory(factory.django.DjangoModelFactory):
    username = fuzzy.FuzzyText(length=50)

    class Meta:
        model = get_user_model()


class PermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permission
        django_get_or_create = ("codename", )

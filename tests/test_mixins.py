from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import resolve, reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

import pytest
from unittest import TestCase

from etools_validator.mixins import ValidatorViewMixin

from demo.factories import DemoChildModelFactory, DemoModelFactory, SpecialModelFactory, UserFactory
from demo.sample.models import DemoChildModel, DemoModel, SpecialModel

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("param", ['', None, 'true', 'false'])
def test_validatorviewmixin(param):
    request = APIRequestFactory()
    request.data = {"sample": param}
    m = ValidatorViewMixin()
    assert m._parse_data(request)


class TestValidatorViewMixin(TestCase):
    def _get_response(self, method, url, data, user=None, format="multipart"):
        user = UserFactory if user is None else user
        factory = APIRequestFactory()
        force_authenticate(user)
        request_call = getattr(factory, method)
        request = request_call(url, data, format=format)
        view = resolve(url)
        return view.func(request, *view.args, **view.kwargs)

    def test_create_fail_validation(self):
        response = self._get_response(
            "post",
            reverse("sample:create"),
            {"name": "New"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"errors": ["demo_validation"]})

    def test_create(self):
        demo_qs = DemoModel.objects.filter(name="New")
        self.assertFalse(demo_qs.exists())
        response = self._get_response(
            "post",
            reverse("sample:create"),
            {
                "name": "New",
                "document": SimpleUploadedFile("test.txt", b"Sample text")
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New")
        self.assertTrue(demo_qs.exists())

    def test_update_fail_validation(self):
        m = DemoModelFactory(name="Old")
        response = self._get_response(
            "put",
            reverse("sample:update", args=[m.pk]),
            {"name": "New"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ["demo_validation"])

    def test_update(self):
        m = DemoModelFactory(name="Old", document="test.txt")
        response = self._get_response(
            "put",
            reverse("sample:update", args=[m.pk]),
            {"name": "New"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], m.pk)
        self.assertEqual(response.data["name"], "New")

    def test_update_children_update(self):
        m = DemoModelFactory(name="Old", document="test.txt")
        child = DemoChildModelFactory(
            parent=m,
            name="Old Child",
        )
        response = self._get_response(
            "put",
            reverse("sample:update", args=[m.pk]),
            {
                "name": "New",
                "children": {
                    "id": child.pk,
                    "parent": m.pk,
                    "name": "Updated Child"
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], m.pk)
        self.assertEqual(response.data["name"], "New")
        child_updated = DemoChildModel.objects.get(pk=child.pk)
        self.assertEqual(child_updated.name, "Updated Child")

    def test_update_special_update(self):
        m = DemoModelFactory(name="Old", document="test.txt")
        special = SpecialModelFactory(
            demo=m,
            name="Old Special",
        )
        response = self._get_response(
            "put",
            reverse("sample:update", args=[m.pk]),
            {
                "name": "New",
                "special": {
                    "id": special.pk,
                    "demo": m.pk,
                    "name": "Updated Special"
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], m.pk)
        self.assertEqual(response.data["name"], "New")
        special_updated = SpecialModel.objects.get(pk=special.pk)
        self.assertEqual(special_updated.name, "Updated Special")

    def test_update_children_create(self):
        m = DemoModelFactory(name="Old", document="test.txt")
        child_qs = DemoChildModel.objects.filter(parent=m)
        self.assertFalse(child_qs.exists())
        response = self._get_response(
            "put",
            reverse("sample:update", args=[m.pk]),
            {
                "name": "Update",
                "children": {
                    "parent": m.pk,
                    "name": "New Child"
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], m.pk)
        self.assertEqual(response.data["name"], "Update")
        self.assertTrue(child_qs.exists())

    def test_update_children_create_invalid(self):
        m = DemoModelFactory(name="Old", document="test.txt")
        child_qs = DemoChildModel.objects.filter(parent=m)
        self.assertFalse(child_qs.exists())
        response = self._get_response(
            "put",
            reverse("sample:update", args=[m.pk]),
            {
                "name": "Update",
                "children": {
                    "parent": m.pk,
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            "children": {"name": ["This field is required."]}
        })
        self.assertFalse(child_qs.exists())

    def test_update_children_invalid_id(self):
        """If invalid id provided for child,
        ignore id then and create new child
        """
        m = DemoModelFactory(name="Old", document="test.txt")
        child_qs = DemoChildModel.objects.filter(parent=m)
        self.assertFalse(child_qs.exists())
        response = self._get_response(
            "put",
            reverse("sample:update", args=[m.pk]),
            {
                "name": "Update",
                "children": {
                    "id": 404,
                    "parent": m.pk,
                    "name": "New Child"
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], m.pk)
        self.assertEqual(response.data["name"], "Update")
        self.assertTrue(child_qs.exists())

    def test_update_children_create_list(self):
        m = DemoModelFactory(name="Old", document="test.txt")
        child_qs = DemoChildModel.objects.filter(parent=m)
        self.assertFalse(child_qs.exists())
        response = self._get_response(
            "put",
            reverse("sample:update", args=[m.pk]),
            {
                "name": "Update",
                "children": [{
                    "parent": m.pk,
                    "name": "Child One"
                }, {
                    "parent": m.pk,
                    "name": "Child Two"
                }]
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], m.pk)
        self.assertEqual(response.data["name"], "Update")
        self.assertTrue(child_qs.exists())
        self.assertEqual(child_qs.count(), 2)

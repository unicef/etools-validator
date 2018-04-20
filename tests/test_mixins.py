from unittest import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import resolve, reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from demo.sample.models import DemoModel
from tests.factories import DemoModelFactory, UserFactory


class TestValidatorViewMixin(TestCase):
    def _get_response(self, method, url, data, user=None):
        user = UserFactory if user is None else user
        factory = APIRequestFactory()
        force_authenticate(user)
        request_call = getattr(factory, method)
        request = request_call(url, data)
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

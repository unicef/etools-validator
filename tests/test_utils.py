from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from unittest import TestCase

from django.utils import six

from demo.sample import models

from validator import utils


class TestGetAllFieldNames(TestCase):
    def test_many(self):
        m = models.DemoModel()
        fields = utils.get_all_field_names(m)
        six.assertCountEqual(self, fields, [
            "id",
            "name",
            "description",
            "document",
            "children",
        ])

    def test_related(self):
        m = models.DemoChildModel()
        fields = utils.get_all_field_names(m)
        six.assertCountEqual(self, fields, [
            "id",
            "name",
            "parent",
            "parent_id",
        ])


class TestCheckEditableFields(TestCase):
    def test_no_old_instance(self):
        m = models.DemoModel()
        self.assertFalse(hasattr(m, "old_instance"))
        editable, fields = utils.check_editable_fields(m, ["name"])
        self.assertFalse(editable)
        self.assertEqual(fields, ["name"])

    def test_editable(self):
        m = models.DemoModel()
        fields = ["name", "description"]
        m.old_instance = models.DemoModel()
        self.assertTrue(hasattr(m, "old_instance"))
        editable, res = utils.check_editable_fields(m, fields)
        self.assertTrue(editable)
        self.assertIsNone(res)

    def test_not_editable(self):
        """Children attribute on demo models do not equal each other
        Results in not editable
        """
        m = models.DemoModel()
        fields = ["children"]
        m.old_instance = models.DemoModel()
        self.assertTrue(hasattr(m, "old_instance"))
        editable, res = utils.check_editable_fields(m, fields)
        self.assertFalse(editable)
        self.assertEqual(res, "children")


class TestCheckRequiredFields(TestCase):
    def test_field_value(self):
        m = models.DemoModel(description="random text")
        fields = ["description"]
        required, field = utils.check_required_fields(m, fields)
        self.assertTrue(required)
        self.assertIsNone(field)

    def test_field_value_blank(self):
        m = models.DemoModel(description="")
        fields = ["description"]
        required, field = utils.check_required_fields(m, fields)
        self.assertTrue(required)
        self.assertIsNone(field)

    def test_field_value_none(self):
        m = models.DemoModel(description=None)
        fields = ["name", "description"]
        required, field = utils.check_required_fields(m, fields)
        self.assertFalse(required)
        self.assertEqual(field, ["description"])

    def test_file_field_value(self):
        m = models.DemoModel(document="random.pdf")
        fields = ["name", "description", "document"]
        required, field = utils.check_required_fields(m, fields)
        self.assertTrue(required)
        self.assertIsNone(field)

    def test_file_field_value_none(self):
        m = models.DemoModel(document=None)
        fields = ["name", "description", "document"]
        required, field = utils.check_required_fields(m, fields)
        self.assertFalse(required)
        self.assertEqual(field, ["document"])


class TestFieldComparison(TestCase):
    def test_simple(self):
        self.assertTrue(utils.field_comparison("1", "1"))

    def test_simple_false(self):
        self.assertFalse(utils.field_comparison("1", 1))

    def test_fields(self):
        m1 = models.DemoModel(name="hello")
        m2 = models.DemoModel(name="hello")
        self.assertTrue(utils.field_comparison(m1.name, m2.name))

    def test_fields_false(self):
        m1 = models.DemoModel(name="hello")
        m2 = models.DemoModel(name="world")
        self.assertFalse(utils.field_comparison(m1.name, m2.name))

    def test_file_fields(self):
        m1 = models.DemoModel(document="sample1.pdf")
        m2 = models.DemoModel(document="sample1.pdf")
        self.assertTrue(utils.field_comparison(m1.document, m2.document))

    def test_file_fields_false(self):
        m1 = models.DemoModel(document="sample1.pdf")
        m2 = models.DemoModel(document="sample2.pdf")
        self.assertFalse(utils.field_comparison(m1.document, m2.document))

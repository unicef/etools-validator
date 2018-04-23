from unittest import TestCase

from demo.sample import models

from tests.factories import DemoChildModelFactory, DemoModelFactory
from validator import utils


class TestGetAllFieldNames(TestCase):
    def test_many(self):
        m = models.DemoModel()
        fields = utils.get_all_field_names(m)
        self.assertCountEqual(fields, [
            "id",
            "name",
            "description",
            "document",
            "status",
            "children",
            "demomodelnoauto"
        ])

    def test_related(self):
        m = models.DemoChildModel()
        fields = utils.get_all_field_names(m)
        self.assertCountEqual(fields, [
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

    def test_file_does_not_exist(self):
        m = models.DemoChildModel(name="Child")
        fields = ["name", "parent"]
        required, field = utils.check_required_fields(m, fields)
        self.assertFalse(required)
        self.assertEqual(field, "parent")


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


class TestCheckRigidRelated(TestCase):
    def test_old_is_none(self):
        """Old instance attribute does not have the related field set
        as <field>_old
        """
        parent = models.DemoModel(name="parent")
        models.DemoChildModel(name="child", parent=parent)
        new = models.DemoModel(name="new parent")
        new.old_instance = parent
        self.assertTrue(utils.check_rigid_related(new, "children"))

    def test_related_different(self):
        """Count on old related field differs with current model"""
        parent1 = models.DemoModel(name="parent1")
        child1 = models.DemoChildModel(name="child1", parent=parent1)
        parent2 = models.DemoModel(name="parent2")
        parent1.children_old = [child1]
        parent2.old_instance = parent1
        self.assertFalse(utils.check_rigid_related(parent2, "children"))

    def test_related_current_empty(self):
        """Count on old related field matches, and current is empty"""
        parent1 = models.DemoModel(name="parent1")
        models.DemoChildModel(name="child1", parent=parent1)
        parent2 = models.DemoModel(name="parent2")
        parent1.children_old = []
        parent2.old_instance = parent1
        self.assertTrue(utils.check_rigid_related(parent2, "children"))


class TestCheckRigidFields(TestCase):
    def test_no_old_instance(self):
        obj = models.DemoModel(name="Object")
        self.assertEqual(utils.check_rigid_fields(obj, ["name"]), (True, None))

    def test_fields_differ(self):
        old = DemoModelFactory(name="Old")
        new = models.DemoModel(name="New")
        new.old_instance = old
        self.assertEqual(
            utils.check_rigid_fields(new, ["name"]),
            (False, "name")
        )

    def test_fields_match(self):
        old = DemoModelFactory(name="Name")
        new = models.DemoModel(name="Name")
        new.old_instance = old
        self.assertEqual(
            utils.check_rigid_fields(new, ["name"]),
            (True, None)
        )

    def test_new_field_does_not_exist(self):
        old = DemoChildModelFactory(name="Old")
        new = models.DemoChildModel(name="New")
        new.old_instance = old
        self.assertEqual(
            utils.check_rigid_fields(new, ["parent"]),
            (False, "parent")
        )

    def test_old_field_does_not_exist(self):
        parent = DemoModelFactory()
        old = models.DemoChildModel(name="Old")
        new = models.DemoChildModel(name="New", parent=parent)
        new.old_instance = old
        self.assertEqual(
            utils.check_rigid_fields(new, ["parent"]),
            (False, "parent")
        )

    def test_field_does_not_exist(self):
        old = models.DemoChildModel(name="Old")
        new = models.DemoChildModel(name="New")
        new.old_instance = old
        self.assertEqual(
            utils.check_rigid_fields(new, ["parent"]),
            (True, None)
        )


class TestUpdateObject(TestCase):
    def test_update(self):
        m = models.DemoModel(name="Old")
        utils.update_object(m, {"name": "New"})
        self.assertEqual(m.name, "New")

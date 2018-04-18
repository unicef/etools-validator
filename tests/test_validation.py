from unittest import TestCase

from demo.sample.models import DemoModel
from demo.sample.permissions import DemoModelValidation

from validator.validation import CompleteValidation
from tests.factories import DemoModelFactory


class TestCompleteValidation(TestCase):
    def test_init_stateless(self):
        new = DemoModel(name="New")
        v = DemoModelValidation(new, stateless=True)
        self.assertEqual(v.new, new)
        self.assertTrue(v.stateless)
        self.assertIsNone(v.user)
        self.assertIsNone(v.old)
        self.assertIsNone(v.permissions)
        self.assertFalse(v.disable_rigid_check)

    def test_init(self):
        new = DemoModel(name="New", status=DemoModel.STATUS_NEW)
        v = DemoModelValidation(new, stateless=False)
        self.assertEqual(v.new, new)
        self.assertFalse(v.stateless)
        self.assertIsNone(v.user)
        self.assertIsNone(v.old)
        self.assertIsNone(v.permissions)
        self.assertFalse(v.disable_rigid_check)
        self.assertEqual(v.new_status, new.status)
        self.assertIsNone(v.old_status)

    def test_init_old_dict(self):
        """Old parameter cannot be a dict, needs to be model instance"""
        new = DemoModel(name="New")
        with self.assertRaisesRegexp(TypeError, "needs to be a model"):
            DemoModelValidation(new, old={"name": "Old"})

    def test_init_new_dict_invalid_validation_class(self):
        class TestValidation(CompleteValidation):
            VALIDATION_CLASS = "wrong.Model"
        with self.assertRaisesRegexp(TypeError, "instance_class is not"):
            TestValidation({"name": "New"})

    def test_init_new_dict_with_id_no_old(self):
        """New in dictionary format, old and instance class not provided
        ensure that new and old attributes set correctly
        """
        m = DemoModelFactory(name="Old")
        v = DemoModelValidation({"name": "New", "id": m.pk}, stateless=True)
        self.assertIsInstance(v.new, DemoModel)
        self.assertEqual(v.new, m)
        self.assertEqual(v.old, m)
        self.assertEqual(v.new.name, "New")
        self.assertEqual(v.old.name, "Old")

    def test_init_new_dict_with_id_no_instance_class(self):
        """New in dictionary format, old provide, not instance_class
        ensure new and old attributes set correctly
        """
        m = DemoModelFactory(name="Old")
        v = DemoModelValidation(
            {"name": "New", "id": m.pk},
            old=m,
            stateless=True
        )
        self.assertIsInstance(v.new, DemoModel)
        self.assertEqual(v.new, m)
        self.assertEqual(v.old, m)
        self.assertEqual(v.new.name, "New")
        self.assertEqual(v.old.name, "Old")

    def test_init_new_dict_with_id(self):
        """New in dictionary format, old and instance class provide
        ensure new and old attributes set correctly
        """
        m = DemoModelFactory(name="Old")
        v = DemoModelValidation(
            {"name": "New", "id": m.pk},
            old=m,
            instance_class=type(m),
            stateless=True
        )
        self.assertIsInstance(v.new, DemoModel)
        self.assertEqual(v.new, m)
        self.assertEqual(v.old, m)
        self.assertEqual(v.new.name, "New")
        self.assertEqual(v.old.name, "Old")

    def test_init_new_dict(self):
        """New in dictionary format without id, old and instance class provide
        ensure new and old attributes set correctly
        """
        m = DemoModelFactory(name="Old")
        v = DemoModelValidation(
            {"name": "New"},
            old=m,
            instance_class=type(m),
            stateless=True
        )
        self.assertIsInstance(v.new, DemoModel)
        self.assertEqual(v.new, m)
        self.assertEqual(v.old, m)
        self.assertEqual(v.new.name, "New")
        self.assertEqual(v.old.name, "Old")
        self.assertEqual(v.new.pk, v.old.pk)

    def test_init_new_dict_no_old(self):
        """New in dictionary format without id, instance class provide, no old
        New attribute is set, while old is None
        """
        m = DemoModelFactory(name="Old")
        v = DemoModelValidation(
            {"name": "New"},
            instance_class=type(m),
            stateless=True
        )
        self.assertIsInstance(v.new, DemoModel)
        self.assertIsNone(v.old)

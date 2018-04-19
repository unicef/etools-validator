from unittest import TestCase

from django.contrib.contenttypes.models import ContentType

from demo.sample.models import DemoModel
from demo.sample.validation import DemoModelValidation
from demo.sample.permissions import DemoModelPermissions

from validator.exceptions import TransitionError
from validator.validation import CompleteValidation
from tests.factories import DemoModelFactory, PermissionFactory, UserFactory


class TestCompleteValidation(TestCase):
    def setUp(self):
        content_type = ContentType.objects.get_for_model(DemoModel)
        self.perm = PermissionFactory(
            codename="can_change_to_pending",
            content_type=content_type,
        )

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

    def test_get_permissions_no_class(self):
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        self.assertIsNone(v.get_permissions(None))

    def test_get_permissions(self):
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        v.PERMISSIONS_CLASS = DemoModelPermissions
        self.assertEqual(v.get_permissions(None), {
            "edit": {
                "name": "edit",
                "description": "edit",
                "status": "edit",
                "document": "edit",
            }
        })

    def test_check_transition_conditions_empty(self):
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        self.assertTrue(v.check_transition_conditions(None))

    def test_check_transition_conditions_false(self):
        m = DemoModelFactory(name="Old")
        new = {"id": m.pk, "name": "New", "status": DemoModel.STATUS_END}
        v = DemoModelValidation(new, old=m, instance_class=DemoModel)
        with self.assertRaisesRegexp(TransitionError, "Document is required"):
            v.check_transition_conditions(v.transition)

    def test_check_transition_conditions(self):
        m = DemoModelFactory(name="Old")
        self.assertEqual(m.status, DemoModel.STATUS_NEW)
        new = {
            "id": m.pk,
            "name": "New",
            "document": "test.pdf",
            "status": DemoModel.STATUS_END
        }
        v = DemoModelValidation(new, old=m, instance_class=DemoModel)
        self.assertIsNotNone(v.transition)
        self.assertTrue(v.check_transition_conditions(v.transition))

    def test_transition_none(self):
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        self.assertIsNone(v.transition)

    def test_transition(self):
        m = DemoModelFactory(name="Old")
        new = {"id": m.pk, "name": "New", "status": DemoModel.STATUS_END}
        v = DemoModelValidation(new, old=m, instance_class=DemoModel)
        self.assertEqual(v.transition, m.complete)

    def test_check_transition_permission_empty(self):
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        self.assertTrue(v.check_transition_permission(None))

    def test_check_transition_permission_false(self):
        user = UserFactory()
        m = DemoModelFactory(name="Old")
        self.assertEqual(m.status, DemoModel.STATUS_NEW)
        new = {
            "id": m.pk,
            "name": "New",
            "document": "test.pdf",
            "status": DemoModel.STATUS_PENDING
        }
        v = DemoModelValidation(new, old=m, user=user)
        self.assertIsNotNone(v.transition)
        self.assertFalse(v.check_transition_permission(v.transition))

    def test_check_transition_permission(self):
        user = UserFactory()
        user.user_permissions.add(self.perm)
        m = DemoModelFactory(name="Old")
        self.assertEqual(m.status, DemoModel.STATUS_NEW)
        new = {
            "id": m.pk,
            "name": "New",
            "document": "test.pdf",
            "status": DemoModel.STATUS_PENDING
        }
        v = DemoModelValidation(new, old=m, user=user)
        self.assertIsNotNone(v.transition)
        self.assertTrue(v.check_transition_permission(v.transition))

    def test_transition_validation_no_permission(self):
        m = DemoModelFactory(name="Old")
        self.assertEqual(m.status, DemoModel.STATUS_NEW)
        new = {
            "id": m.pk,
            "name": "New",
            "document": "test.pdf",
            "status": DemoModel.STATUS_PENDING
        }
        v = DemoModelValidation(new, old=m)
        self.assertTrue(v.skip_permissions)
        self.assertTrue(v.transitional_validation())

    def test_transition_validation(self):
        user = UserFactory()
        user.user_permissions.add(self.perm)
        m = DemoModelFactory(name="Old")
        self.assertEqual(m.status, DemoModel.STATUS_NEW)
        new = {
            "id": m.pk,
            "name": "New",
            "document": "test.pdf",
            "status": DemoModel.STATUS_PENDING
        }
        v = DemoModelValidation(new, old=m, user=user)
        self.assertFalse(v.skip_permissions)
        self.assertTrue(v.transitional_validation())

    def test_basic_validation_empty(self):
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        v.BASIC_VALIDATIONS = []
        self.assertEqual(v.basic_validation, (True, []))

    def test_basic_validation(self):
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        self.assertEqual(v.basic_validation, (False, ["demo_validation"]))

    def test_state_valid_no_basic_validations(self):
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        v.BASIC_VALIDATIONS = []
        self.assertTrue(v.state_valid())

    def test_state_valid(self):
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        self.assertEqual(
            v.state_valid(),
            (False, ["generic_state_validation_fail"])
        )

    def test_state_valid_func(self):
        user = UserFactory()
        new = {"name": "New", "status": DemoModel.STATUS_PENDING}
        v = DemoModelValidation(new, user=user, instance_class=DemoModel)
        v.BASIC_VALIDATIONS = []
        self.assertEqual(
            v.state_valid(),
            (False, ["generic_state_validation_fail"])
        )

    def test_auto_transition_validation_false(self):
        m = DemoModelFactory(name="Old")
        new = {"id": m.pk, "name": "New", "status": DemoModel.STATUS_END}
        v = DemoModelValidation(new, old=m)
        self.assertEqual(
            v.auto_transition_validation(v.transition),
            (False, ["Document is required"])
        )

    def test_auto_transition_validation(self):
        m = DemoModelFactory(name="Old")
        self.assertEqual(m.status, DemoModel.STATUS_NEW)
        new = {
            "id": m.pk,
            "name": "New",
            "document": "test.pdf",
            "status": DemoModel.STATUS_END
        }
        v = DemoModelValidation(new, old=m)
        self.assertTrue(v.auto_transition_validation(v.transition))

    def test_first_available_auto_transition_empty(self):
        DemoModel.AUTO_TRANSITIONS = {}
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        self.assertEqual(
            v._first_available_auto_transition(),
            (None, None, None)
        )

    def test_first_available_auto_transition(self):
        old = DemoModelFactory(name="Old")
        new = {"name": "New"}
        v = DemoModelValidation(new, old=old)
        self.assertEqual(
            v._first_available_auto_transition(),
            (True, "pending", [])
        )

    def test_make_auto_transition_none(self):
        DemoModel.AUTO_TRANSITIONS = {}
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        self.assertFalse(v._make_auto_transition())

    def test_map_errors(self):
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        self.assertEqual(v.map_errors(["wrong"]), ["Things went wrong"])

    def test_map_errors_not_found(self):
        v = DemoModelValidation({"name": "New"}, instance_class=DemoModel)
        self.assertEqual(v.map_errors(["unknown"]), ["unknown"])

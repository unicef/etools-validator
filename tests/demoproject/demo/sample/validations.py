from etools_validator.exceptions import StateValidationError
from etools_validator.utils import check_rigid_fields
from etools_validator.validation import CompleteValidation

from .permissions import DemoModelPermissions


def demo_validation(instance):
    return bool(instance.document)


class DemoModelValidation(CompleteValidation):
    VALIDATION_CLASS = "sample.DemoModel"
    BASIC_VALIDATIONS = [demo_validation]
    VALID_ERRORS = {
        "wrong": "Things went wrong"
    }

    def state_pending_valid(self, instance, user):
        if user.is_staff:
            return True
        return False


class ProtectedDemoModelValidation(DemoModelValidation):
    PERMISSIONS_CLASS = DemoModelPermissions

    def check_rigid_fields(self, assessment, related=False):
        # this can be set if running in a task and old_instance is not set
        if self.disable_rigid_check:
            return
        rigid_fields = [
            f for f in self.permissions['edit']
            if self.permissions['edit'][f] is False
        ]
        rigid_valid, field = check_rigid_fields(
            assessment,
            rigid_fields,
            related=related,
        )
        if not rigid_valid:
            raise StateValidationError(
                ['Cannot change fields while in {}: {}'.format(
                    assessment.status,
                    field,
                )]
            )

    def state_new_valid(self, instance, user=None):
        self.check_rigid_fields(instance, related=True)
        return True

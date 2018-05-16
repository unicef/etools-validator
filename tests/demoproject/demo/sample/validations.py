from etools_validator.validation import CompleteValidation


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

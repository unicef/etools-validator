from .exceptions import (
    BasicValidationError,
    DetailedBasicValidationError,
    DetailedStateValidationError,
    DetailedTransitionError,
    StateValidationError,
    TransitionError,
)


def error_data(function):
    def wrapper(*args, **kwargs):
        try:
            valid = function(*args, **kwargs)
        except BasicValidationError as e:
            return (False, [str(e)])
        except DetailedBasicValidationError as e:
            return (False, [e.details])
        else:
            if valid and type(valid) is bool:
                return (True, [])
            else:
                return (False, [function.__name__])

    return wrapper


def transition_error_data(function):
    def wrapper(*args, **kwargs):
        try:
            valid = function(*args, **kwargs)
        except TransitionError as e:
            return (False, [str(e)])
        except DetailedTransitionError as e:
            return (False, [e.details])

        if valid and type(valid) is bool:
            return (True, [])
        else:
            return (False, ['generic_transition_fail'])

    return wrapper


def state_error_data(function):
    def wrapper(*args, **kwargs):
        try:
            valid = function(*args, **kwargs)
        except StateValidationError as e:
            return (False, [str(e)])
        except DetailedStateValidationError as e:
            return (False, [e.details])

        if valid and type(valid) is bool:
            return (True, [])
        else:
            return (False, ['generic_state_validation_fail'])

    return wrapper

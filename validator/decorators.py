from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils import six

from validator.exceptions import (
    BasicValidationError,
    StateValidationError,
    TransitionError
)


def error_string(function):
    def wrapper(*args, **kwargs):
        try:
            valid = function(*args, **kwargs)
        except BasicValidationError as e:
            return (False, [six.text_type(e)])
        else:
            if valid and type(valid) is bool:
                return (True, [])
            else:
                return (False, [function.__name__])
    return wrapper


def transition_error_string(function):
    def wrapper(*args, **kwargs):
        try:
            valid = function(*args, **kwargs)
        except TransitionError as e:
            return (False, [six.text_type(e)])

        if valid and type(valid) is bool:
            return (True, [])
        else:
            return (False, ['generic_transition_fail'])
    return wrapper


def state_error_string(function):
    def wrapper(*args, **kwargs):
        try:
            valid = function(*args, **kwargs)
        except StateValidationError as e:
            return (False, [six.text_type(e)])

        if valid and type(valid) is bool:
            return (True, [])
        else:
            return (False, ['generic_state_validation_fail'])
    return wrapper

from unittest import TestCase
from unittest.mock import Mock

from etools_validator import decorators
from etools_validator.exceptions import BasicValidationError, StateValidationError, TransitionError


class TestErrorString(TestCase):
    def test_error(self):
        func = Mock(side_effect=BasicValidationError("Oops"))
        res = decorators.error_string(func)()
        self.assertEqual(res, (False, ["Oops"]))

    def test_valid_bool(self):
        func = Mock(return_value=True)
        res = decorators.error_string(func)()
        self.assertEqual(res, (True, []))

    def test_valid(self):
        def func():
            return "string"
        res = decorators.error_string(func)()
        self.assertEqual(res, (False, ["func"]))


class TestTransitionErrorString(TestCase):
    def test_error(self):
        func = Mock(side_effect=TransitionError(["Oops"]))
        res = decorators.transition_error_string(func)()
        self.assertEqual(res, (False, ["Oops"]))

    def test_valid_bool(self):
        func = Mock(return_value=True)
        res = decorators.transition_error_string(func)()
        self.assertEqual(res, (True, []))

    def test_valid(self):
        def func():
            return "string"
        res = decorators.transition_error_string(func)()
        self.assertEqual(res, (False, ["generic_transition_fail"]))


class TestStateErrorString(TestCase):
    def test_error(self):
        func = Mock(side_effect=StateValidationError(["Oops"]))
        res = decorators.state_error_string(func)()
        self.assertEqual(res, (False, ["Oops"]))

    def test_valid_bool(self):
        func = Mock(return_value=True)
        res = decorators.state_error_string(func)()
        self.assertEqual(res, (True, []))

    def test_valid(self):
        def func():
            return "string"
        res = decorators.state_error_string(func)()
        self.assertEqual(res, (False, ["generic_state_validation_fail"]))

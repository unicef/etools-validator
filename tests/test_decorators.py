from unittest import TestCase
from unittest.mock import Mock

from etools_validator import decorators
from etools_validator.exceptions import (
    BasicValidationError,
    DetailedBasicValidationError,
    DetailedStateValidationError,
    DetailedTransitionError,
    StateValidationError,
    TransitionError,
)


class TestError(TestCase):
    def test_error_string(self):
        func = Mock(side_effect=BasicValidationError("Oops"))
        res = decorators.error_data(func)()
        self.assertEqual(res, (False, ["Oops"]))

    def test_error_details(self):
        func = Mock(side_effect=DetailedBasicValidationError("test_code", "Oops"))
        res = decorators.error_data(func)()
        self.assertEqual(res, (False, [{"code": "test_code", "description": "Oops", "extra": {}}]))

    def test_valid_bool(self):
        func = Mock(return_value=True)
        res = decorators.error_data(func)()
        self.assertEqual(res, (True, []))

    def test_valid(self):
        def func():
            return "string"
        res = decorators.error_data(func)()
        self.assertEqual(res, (False, ["func"]))


class TestTransitionError(TestCase):
    def test_error_string(self):
        func = Mock(side_effect=TransitionError(["Oops"]))
        res = decorators.transition_error_data(func)()
        self.assertEqual(res, (False, ["Oops"]))

    def test_error_details(self):
        func = Mock(side_effect=DetailedTransitionError("test_code_transition", "Oops"))
        res = decorators.transition_error_data(func)()
        self.assertEqual(res, (False, [{"code": "test_code_transition", "description": "Oops", "extra": {}}]))

    def test_valid_bool(self):
        func = Mock(return_value=True)
        res = decorators.transition_error_data(func)()
        self.assertEqual(res, (True, []))

    def test_valid(self):
        def func():
            return "string"
        res = decorators.transition_error_data(func)()
        self.assertEqual(res, (False, ["generic_transition_fail"]))


class TestStateError(TestCase):
    def test_error_string(self):
        func = Mock(side_effect=StateValidationError(["Oops"]))
        res = decorators.state_error_data(func)()
        self.assertEqual(res, (False, ["Oops"]))

    def test_error_details(self):
        func = Mock(side_effect=DetailedStateValidationError("test_code_state", "Oops"))
        res = decorators.state_error_data(func)()
        self.assertEqual(res, (False, [{"code": "test_code_state", "description": "Oops", "extra": {}}]))

    def test_valid_bool(self):
        func = Mock(return_value=True)
        res = decorators.state_error_data(func)()
        self.assertEqual(res, (True, []))

    def test_valid(self):
        def func():
            return "string"
        res = decorators.state_error_data(func)()
        self.assertEqual(res, (False, ["generic_state_validation_fail"]))

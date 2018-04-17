from unittest import TestCase

from validator.exceptions import (
    _BaseStateError,
    BasicValidationError,
    StateValidationError,
    TransitionError,
)


class TestExceptions(TestCase):
    '''Tests behavior of the 3 exceptions defined in validation_mixins.

    StateValidError and TransitionError are tested through their base
    class _BaseStateError.
    '''
    def test_basic_validation_error(self):
        '''Exercise converting BasicValidationError to string'''
        e = BasicValidationError()
        self.assertEqual(str(e), '')

        e = BasicValidationError('hello world')
        self.assertEqual(str(e), 'hello world')

    def test_state_valid_error(self):
        '''Ensure StateValidError inherits from _BaseStateError'''
        self.assertIsInstance(StateValidationError(), _BaseStateError)

    def test_transition_valid_error(self):
        '''Ensure TransitionError inherits from _BaseStateError'''
        self.assertIsInstance(TransitionError(), _BaseStateError)

    def test_base_state_error_stringification(self):
        '''Exercise converting _BaseStateError to a string'''
        e = _BaseStateError()
        self.assertEqual(str(e), '')

        e = _BaseStateError(['hello world'])
        self.assertEqual(str(e), 'hello world')

        # Test non-ASCII unicode in the params
        e = _BaseStateError([
            'hello world',
            'goodbye world',
            u'l\xf6rem ipsum',
            u'l\xf6rem ipsum'
        ])
        self.assertEqual(
            str(e),
            u'hello world\ngoodbye world\nl\xf6rem ipsum\nl\xf6rem ipsum'
        )

    def test_base_state_error_creation(self):
        '''Exercise _BaseStateError creation.
        _BaseStateError accepts only one param, and it must be a list.'''
        for param in ('hello world',
                      ('hello world', 'goodbye world'),
                      42,
                      object(),
                      TestCase,):
            with self.assertRaises(TypeError):
                _BaseStateError(param)

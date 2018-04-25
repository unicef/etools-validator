class _BaseStateError(BaseException):
    '''Base class for state-related exceptions.
    Accepts only one param which must be a list of strings.'''
    def __init__(self, message=None):
        message = message or []
        if not isinstance(message, list):
            raise TypeError('{} takes a list of errors not {}'.format(
                self.__class__,
                type(message)
            ))
        super(_BaseStateError, self).__init__(message)

    def __str__(self):
        return '\n'.join([str(msg) for msg in self.args[0]])


class TransitionError(_BaseStateError):
    pass


class StateValidationError(_BaseStateError):
    pass


class BasicValidationError(BaseException):
    def __init__(self, message=''):
        super(BasicValidationError, self).__init__(message)

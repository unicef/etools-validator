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


class BaseDetailedError(BaseException):
    """
    Base class for detailed validation exceptions.
    It contains full information about error: code, description and extra data
    """

    def __init__(self, code: str, description: str, extra: dict = None):
        super().__init__(self)
        self.code = code
        self.description = description
        self.extra = extra or {}

    def __str__(self):
        return self.description

    @property
    def details(self):
        return {
            'code': self.code,
            'description': self.description,
            'extra': self.extra,
        }


class DetailedBasicValidationError(BaseDetailedError):
    pass


class DetailedTransitionError(BaseDetailedError):
    pass


class DetailedStateValidationError(BaseDetailedError):
    pass

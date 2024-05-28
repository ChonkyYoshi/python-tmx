class MissingAttributeError(Exception):
    """Raised when trying to serialize an object with missing required attributes"""


class InccorectTagError(Exception):
    """Raised when an incorrect tag is encountered when building an object"""


class NonEmptyTagError(Exception):
    """Raised if a tag that's supposed to be empty has text or children"""

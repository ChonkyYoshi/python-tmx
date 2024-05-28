class TagError(Exception):
    """Base class for all tag errors encountered during parsing a tmx file"""


class InccorectTagError(TagError):
    """Raised when an incorrect tag is encountered when building an object"""


class NonEmptyTagError(TagError):
    """Raised if a tag that's supposed to be empty has text or children"""

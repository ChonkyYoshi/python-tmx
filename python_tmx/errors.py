from xml.etree.ElementTree import Element


class TmxError(Exception):
    """base class for all Custom Errors"""


class InccorectTagError(TmxError):
    """Error raised when an incorrect tag is encountered when building an object"""

    def __init__(self, *args: object, element: Element) -> None:
        super().__init__(*args)
        self.element = element

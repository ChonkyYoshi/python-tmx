from xml.etree.ElementTree import Element


class TmxParseError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class IncorrectTagError(Exception):
    def __init__(self, found_element: Element, expected_element: str) -> None:
        super().__init__(
            f"Expected {expected_element} Element but found {found_element.tag} instead"
        )


class ExtraChildrenError(Exception):
    def __init__(self, element: Element) -> None:
        if len(element):
            super().__init__(
                f"Element {element.tag} is not allowed to have children but element has {len(element)} children"
            )


class ExtraTextError(Exception):
    def __init__(self, element: Element) -> None:
        if len(element):
            super().__init__(
                f"Element {element.tag} is not allowed to have text but element has the following text data:\n{element.tail}"
            )


class MissingRequiredAttributeError(Exception):
    def __init__(self, element: Element, attribute: str) -> None:
        super().__init__(
            f"Element {element.tag} is missing required attribute {attribute}"
        )

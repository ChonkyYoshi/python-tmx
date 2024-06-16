__all__ = [
    "IncorrectTagError",
    "RequiredAttributeError",
]


class IncorrectTagError(Exception):
    def __init__(self, found_element: str, expected_element: str) -> None:
        super().__init__(
            f"Expected {expected_element} Element but found {found_element} instead"
        )


class RequiredAttributeError(Exception):
    def __init__(self, element: str, attribute: str) -> None:
        super().__init__(
            f"Element {element.tag} is missing required attribute {attribute}"
        )

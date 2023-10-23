"""segment module"""
from typing import Literal
import lxml.etree as et


class text_run:
    """lowest level element, only contain text."""

    def __init__(self, text: str | None = None) -> None:
        self.text: str | None = text


class bpt_run:
    """corresponds to a <bpt> tag."""

    def __init__(
        self,
        i: int | str,
        tagged_text: str | None = None,
        x: int | str | None = None,
        data_type: str | None = None,
    ) -> None:
        self.tagged_text: str | None = tagged_text
        self.i: int | str = i
        self.x: int | str | None = x
        self.data_type: str | None = data_type


class ept_run:
    """corresponds to a <ept> tag."""

    def __init__(
        self,
        i: int | str,
        tagged_text: str | None = None,
    ) -> None:
        self.tagged_text: str | None = tagged_text
        self.i: int | str = i


class isolated_run:
    """corresponds to a <it> tag."""

    def __init__(self, pos: Literal["begin", "end"] = "end") -> None:
        self.pos: str = pos


class placeholder_run:
    """corresponds to a <ph> tag."""

    def __init__(
        self,
        tagged_text: str | None = None,
        x: int | str | None = None,
        data_type: str | None = None,
        assoc: str | None = None,
    ) -> None:
        self.tagged_text: str | None = tagged_text
        self.x: int | str | None = x
        self.data_type: str | None = data_type
        self.assoc: str | None = assoc


class highlight_run:
    """coresponds to a <hi> tag"""

    def __init__(
        self,
        text: str | None = None,
        x: int | str | None = None,
        data_type: str | None = None,
    ) -> None:
        self.text: str | None = text
        self.x: int | str | None = x
        self.data_type: str | None = data_type


class segment:
    """Segment object, can contain zero, one or more of:
    -   text_run
    -   bpt_run | ept_run
    -   isolated_run
    -   placeholder_run
    -   highlight_run
    Order of the element is significant as it will be retained during export
    If parsing from a file, any element not defined in the TMX DTD will be wrapped in a placeholder_run.
    """

    def __init__(
        self,
        content: list[
            text_run
            | bpt_run
            | ept_run
            | isolated_run
            | placeholder_run
            | highlight_run
        ] = list(),
        xml: et._Element | None = None,
    ) -> None:
        self.content: list[
            text_run
            | bpt_run
            | ept_run
            | isolated_run
            | placeholder_run
            | highlight_run
        ] = content
        self._seg: et._Element | None = xml

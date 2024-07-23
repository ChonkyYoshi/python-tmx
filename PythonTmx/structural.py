from typing import Optional, overload

from lxml.etree import _Element

from PythonTmx.core import TmxAttributes, TmxElement


class Prop(TmxElement):
    type: str
    xmllang: Optional[str]
    oencoding: Optional[str]
    _attributes = (TmxAttributes.type, TmxAttributes.xmllang, TmxAttributes.oencoding)

    @overload
    def __init__(self, *, source_element: _Element | None = None, **kwargs) -> None: ...
    @overload
    def __init__(self, *, content: str | None = None, **kwargs) -> None: ...
    @overload
    def __init__(self, *, type: str = "unknown", **kwargs) -> None: ...
    @overload
    def __init__(self, *, xmllang: str | None = None, **kwargs) -> None: ...
    @overload
    def __init__(self, *, oencoding: str | None = None, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        source_element: Optional[_Element] = kwargs.get("source_element", None)
        self.content: list = []
        if source_element is not None:
            for attribute in self._attributes:
                element_value: Optional[str] = source_element.get(attribute.value)
                if element_value is None:
                    self.__setattr__(attribute.name, kwargs.get(attribute.name, None))
                else:
                    self.__setattr__(attribute.name, element_value)
            if source_element.text is not None:
                self.content.append(source_element.text)
            else:
                if kwargs.get("content") is not None:
                    self.content.append(kwargs["content"])

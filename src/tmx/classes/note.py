class note:
    __slots__ = ["text", "xmllang", "oencoding"]

    def __init__(self, text: str, **kwargs) -> None:
        for attr in self.__slots__:
            if attr in kwargs.keys():
                self.__setattr__(attr, kwargs[attr])
            else:
                self.__setattr__(attr, None)
        self.text = text

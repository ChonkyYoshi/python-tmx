from enum import Enum


class TagType(Enum):
    BPT = "bpt"
    EPT = "ept"
    PH = "ph"
    IT = "it"
    HI = "hi"


class Assoc(Enum):
    P = "p"
    F = "f"
    B = "b"


class Pos(Enum):
    BEGIN = "begin"
    END = "end"


class Segtype(Enum):
    BLOCK = "block"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    PHRASE = "phrase"

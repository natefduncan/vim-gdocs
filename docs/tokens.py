from dataclasses import dataclass, field
from typing import List

class Token:
    pass

#  @dataclass
#  class Color:
    #  red: float
    #  green: float
    #  blue: float

@dataclass
class TextStyle:
    bold: bool = False
    italic: bool = False
    underline: bool = False
    #  foreground_color: Color = Color(0,0,0)

@dataclass
class Text(Token):
    start_index: int
    end_index: int
    text: str
    style: TextStyle 

    def __repr__(self) -> str:
        clean_text = self.text.replace("\n", "\\n")
        return f"Text(\"{clean_text}\", {self.start_index}, {self.end_index})"

@dataclass
class Link(Token):
    start_index: int
    end_index: int
    text: str
    url: str
    style: TextStyle

    def __repr__(self) -> str:
        clean_text = self.text.replace("\n", "\\n")
        return f"Link(\"{clean_text}\", {self.start_index}, {self.end_index})"

@dataclass
class ListItem(Token):
    start_index: int
    end_index: int
    text: str

@dataclass
class List(Token):
    start_index: int
    end_index: int
    list_id: str
    ordered: bool
    items: List[ListItem] = field(default_factory=list)

@dataclass
class SectionBreak:
    end_index: int

@dataclass
class CarriageReturn(Token):
    start_index: int
    end_index: int

    def __repr__(self) -> str:
        return f"CR({self.start_index}, {self.end_index})"

@dataclass
class Header(Token):
    start_index: int
    end_index: int
    level: int
    text: str

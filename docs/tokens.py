from dataclasses import dataclass, field
from typing import List

class Token:
    pass

@dataclass
class TextStyle:
    bold: bool = False
    italic: bool = False
    underline: bool = False

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

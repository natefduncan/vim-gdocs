from typing import List
from docs.tokens import Token, CarriageReturn, Text

class Compiler:
    pass

class Markdown(Compiler):
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def compile(self) -> str:
        text = ""
        for token in self.tokens:
            if isinstance(token, CarriageReturn):
                text += "\n"
            elif isinstance(token, Text):
                formatted_text = token.text
                if token.style.bold:
                    formatted_text = f"**{formatted_text}**"
                if token.style.italic:
                    formatted_text = f"*{formatted_text}*"
                if token.style.underline:
                    formatted_text = f"<u>{formatted_text}</u>"
                text += formatted_text
        return text

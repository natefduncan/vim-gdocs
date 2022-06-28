from typing import List
from docs.diff import generate_delete
from docs.tokens import Token, CarriageReturn, Text, Header

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

class Google(Compiler):
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def compile(self) -> List[dict]:
        requests = []
        #  requests.append(self.generate_delete(self.tokens[0].start_index, self.tokens[-1].end_index))
        for token in self.tokens:
            if isinstance(token, Text):
                requests += self.generate_insert(token)
            elif isinstance(token, CarriageReturn):
                requests.append({ 
                    "insertText": {
                        "location": {
                            "index": token.start_index
                            }, 
                        "text": "\n"
                        }
                    }
                )
            elif isinstance(token, Header):
                pass
        return requests

    @staticmethod
    def generate_delete(start_index, end_index):
        return {
                "deleteContentRange": {
                    "range" : {
                        "endIndex": end_index, 
                        "startIndex": start_index
                        }
                    }
                }

    @staticmethod
    def generate_insert(token):
        output = []
        output.append({
                "insertText": {
                    "location": {
                        "index": token.start_index
                        }, 
                    "text" : token.text
                    }
                })
        output.append({
            "updateTextStyle": {
                "fields" : "*", 
                "range": {
                    "startIndex": token.start_index, 
                    "endIndex": token.end_index
                    }, 
                "textStyle": {
                    "bold": token.style.bold, 
                    "italic": token.style.italic, 
                    "underline": token.style.underline
                    }
                }
            })
        return output 

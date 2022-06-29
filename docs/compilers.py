from typing import List as TList
from docs.diff import generate_delete
from docs.tokens import Token, CarriageReturn, Text, Header, Link, List, ListItem

class Compiler:
    pass

class Markdown(Compiler):
    def __init__(self, tokens: TList[Token]):
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
            elif isinstance(token, Link):
                text += f"[{token.text}]({token.url})"
            elif isinstance(token, List):
                for i, list_item in enumerate(token.items):
                    if token.ordered:
                        text += f"{i}. {list_item.text}\n"
                    else:
                        text += f"- {list_item.text}\n"
        return text

class Google(Compiler):
    def __init__(self, tokens: TList[Token]):
        self.tokens = tokens

    def compile(self) -> TList[dict]:
        requests = []
        for token in self.tokens:
            if isinstance(token, Text):
                requests += self.generate_insert(token)
            elif isinstance(token, Link):
                requests += self.generate_insert(token, is_link=True)
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
    def generate_insert(token, is_link=False):
        output = []
        output.append({
                "insertText": {
                    "location": {
                        "index": token.start_index
                        }, 
                    "text" : token.text
                    }
                })
        styling = {
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
            }
        if is_link:
            styling["updateTextStyle"]["textStyle"]["link"] = {"url": token.url}
            styling["updateTextStyle"]["textStyle"]["foregroundColor"] = {
                    "color": {
                        "rgbColor": {
                            "red": 0.06666667, 
                            "green": 0.33333334, 
                            "blue": 0.8
                            }
                        }
                    }
        output.append(styling)
        return output

    @staticmethod
    def sort_batch_updates(obj):
        if "deleteContentRange" in obj:
            return obj["deleteContentRange"]["range"]["endIndex"]
        elif "insertText" in obj:
            return obj["insertText"]["location"]["index"]
        elif "updateTextStyle" in obj:
            return obj["updateTextStyle"]["range"]["endIndex"]

 

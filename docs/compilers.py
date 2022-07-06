from typing import List as TList
from docs.diff import generate_delete
from docs.tokens import Token, CarriageReturn, Text, Header, Link, List, ListItem, Tab

class Compiler:
    pass

class Markdown(Compiler):
    def __init__(self, tokens: TList[Token]):
        self.tokens = tokens
    
    @staticmethod
    def format_text(token: Text) -> str:
        formatted_text = token.text
        if token.style.bold:
            formatted_text = f"**{formatted_text}**"
        if token.style.italic:
            formatted_text = f"*{formatted_text}*"
        if token.style.underline:
            formatted_text = f"<u>{formatted_text}</u>"
        return formatted_text
 
    @staticmethod
    def format_token(token: Token) -> str:
        if isinstance(token, CarriageReturn):
            return "\n"
        elif isinstance(token, Text):
            return Markdown.format_text(token)
        elif isinstance(token, Link):
            return f"[{token.text}]({token.url})"
        else:
            return ""
        #  elif isinstance(token, Tab):
            #  return "\t"

    @staticmethod
    def format_tokens(tokens: TList[Token]) -> str:
        text = ""
        for token in tokens:
            text += Markdown.format_token(token)
        return text

    def compile(self) -> str:
        text = ""
        for token in self.tokens: 
            if isinstance(token, List):
                for i, list_item in enumerate(token.items):
                    formatted_list_item = self.format_tokens(list_item.text)
                    if token.ordered:
                         text += f"{i}. {formatted_list_item}"
                    else:
                        text += f"- {formatted_list_item}"
            else:
                text += self.format_token(token)
        return text

class Google(Compiler):
    def __init__(self, tokens: TList[Token]):
        self.tokens = tokens

    def compile(self) -> TList[dict]:
        requests = []
        list_id = 0
        for token in self.tokens:
            if isinstance(token, List):
                for list_entry in token.items:
                    for sub_token in list_entry.text:
                        requests += Google.generate_insert(sub_token)
                    requests += [self.generate_bullet(list_entry, token.ordered)]
                list_id += 1
            else:
                requests += self.generate_insert(token)
        return requests

    @staticmethod
    def generate_carriage_return(start_index):
        return {
                "insertText": {
                    "location": {
                        "index": start_index
                        }, 
                    "text": "\n"
                    }
                }

    @staticmethod
    def generate_tab(start_index):
        return {
                "insertText": {
                    "location": {
                        "index": start_index
                        }, 
                    "text": "\t"
                    }
                }

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
    def generate_insert_text(token):
        return {
                "insertText": {
                    "location": {
                        "index": token.start_index
                        }, 
                    "text" : token.text
                    }
                }

    @staticmethod
    def generate_styling(token):
        return {
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

    @staticmethod
    def add_link(styling, url):
        styling["updateTextStyle"]["textStyle"]["link"] = {"url": url}
        styling["updateTextStyle"]["textStyle"]["foregroundColor"] = {
                "color": {
                    "rgbColor": {
                        "red": 0.06666667, 
                        "green": 0.33333334, 
                        "blue": 0.8
                        }
                    }
                }
        return styling

    @staticmethod
    def generate_bullet(token, ordered):
        return {
                "createParagraphBullets": {
                    "range": {
                        "startIndex": token.start_index, 
                        "endIndex": token.start_index + 1
                        }, 
                    "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN" if ordered else "BULLET_DISC_CIRCLE_SQUARE" 
                    }
                }

    @staticmethod
    def generate_named_range(name, start_index, end_index):
        return {
                "createNamedRange": {
                    "range": {
                        "startIndex": start_index,
                        "endIndex": end_index, 
                    }, 
                    "name": name
                    }
                }

    @staticmethod
    def generate_insert(token):
        output = []
        if isinstance(token, Text):
            output.append(Google.generate_insert_text(token))
            output.append(Google.generate_styling(token))
        elif isinstance(token, Link):
            output.append(Google.generate_insert_text(token))
            styling = Google.generate_styling(token)
            styling = Google.add_link(styling, token.url)
            output.append(styling) 
        elif isinstance(token, CarriageReturn):
            output.append(Google.generate_carriage_return(token.start_index))
        elif isinstance(token, Tab):
            output.append(Google.generate_tab(token.start_index))
        return output

    @staticmethod
    def sort_batch_updates(obj):
        if "deleteContentRange" in obj:
            return obj["deleteContentRange"]["range"]["endIndex"]
        elif "insertText" in obj:
            return obj["insertText"]["location"]["index"]
        elif "updateTextStyle" in obj:
            return obj["updateTextStyle"]["range"]["endIndex"]

 

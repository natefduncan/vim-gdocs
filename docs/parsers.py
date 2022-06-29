from typing import List as TList
from docs.tokens import Token, Text, TextStyle, CarriageReturn, Header, Link, List, ListItem
import re

class Parser:
    pass

class Google(Parser):
    def __init__(self, doc):
        self.doc = doc

    def parse_paragraph(self, paragraph) -> TList[Token]:
        tokens = []
        for i in paragraph["paragraph"]["elements"]:
            if i["textRun"]["content"] == "\n":
                tokens.append(CarriageReturn(i["startIndex"], i["endIndex"]))
                text = i["textRun"]["content"]
            elif "link" in i["textRun"]["textStyle"]:
                start_index = i["startIndex"]
                end_index = i["endIndex"]
                text = i["textRun"]["content"]
                url = i["textRun"]["textStyle"]["link"]["url"]
                style=TextStyle(
                        i["textRun"]["textStyle"].get("bold", False), 
                        i["textRun"]["textStyle"].get("italic", False), 
                        i["textRun"]["textStyle"].get("underline", False)
                        )
                
                tokens.append(Link(start_index, end_index, text, url, style))
            elif paragraph["paragraph"].get("bullet"):
                text = i["textRun"]["content"].replace("\n", "")
                start_index = i["startIndex"]
                end_index = i["endIndex"]
                list_id = paragraph['paragraph']["bullet"]["listId"]
                list_item = ListItem(start_index, end_index, text)
                list_token = next((i for i in self.tokens if isinstance(i, List) and i.list_id == list_id), None)
                if list_token:
                    list_token.items.append(list_item)
                    list_token.end_index = end_index
                else:
                    ordered = self.doc["lists"][list_id]["listProperties"]["nestingLevels"][0].get("glyphType") != None
                    list_token = List(start_index, end_index, list_id=list_id, ordered=ordered, items=[list_item])
                    tokens.append(list_token)
            else:
                cr = "\n" in i["textRun"]["content"]
                if cr:
                    end_index = i["endIndex"]-1
                    text = i["textRun"]["content"].replace("\n", "")
                else:
                    text = i["textRun"]["content"]
                    end_index = i["endIndex"]
                tokens.append(
                    Text(
                        start_index=i["startIndex"], 
                        end_index=end_index, 
                        text=text,  
                        style=TextStyle(
                            i["textRun"]["textStyle"].get("bold", False), 
                            i["textRun"]["textStyle"].get("italic", False), 
                            i["textRun"]["textStyle"].get("underline", False)
                            )
                        ) 
                    )
                if cr: 
                    tokens.append(CarriageReturn(i["endIndex"]-1, i["endIndex"]))
        return tokens

    def parse(self) -> TList[Token]:
        content = self.doc.get("body").get("content")
        self.tokens = []
        for e in content:
            if 'paragraph' in e:
                self.tokens += self.parse_paragraph(e)
        return self.tokens

#  https://github.com/yhfyhf/Markdown-Parser-Python/blob/master/parser.py
class Markdown(Parser):
    def __init__(self, markdown_text):
        self.text = markdown_text
        self.token_spec = [
                ("HEADER", r'^#{1,6}\s.+#*'), 
                ("BOLD", r'\*\*([^\*]+)\*\*'), 
                ("ITALIC", r'\*([^\*]+)\*'),
                ("BOLD_ITALIC", r'\*\*\*([^\*]+)\*\*\*'), 
                ("NEWLINE", r'\n'),
                ("LINK", r'\[(.*?)\]\((.*?)\)'), 
                ("UNORDERED_LIST_ITEM", r'\s*- (.*)\s*'), 
                ("NORMAL", r'[\w ]+'), 
                ("SYMBOL", r'.')
        ]
 
    def parse(self):
        token_re = "|".join(f'(?P<{name}>{regex})' for name, regex in self.token_spec)
        start_index = 1
        tokens = []
        list_id = 0
        for mo in re.finditer(token_re, self.text):
            kind = mo.lastgroup
            value = mo.group()
            if kind in ["BOLD", "ITALIC", "BOLD_ITALIC", "NORMAL", "SYMBOL"]:
                is_bold = kind in ["BOLD", "BOLD_ITALIC"]
                is_italic = kind in ["ITALIC", "BOLD_ITALIC"]
                text = value.replace("*", "")
                end_index = start_index + len(text)
                tokens.append(Text(start_index, end_index, text, TextStyle(bold=is_bold, italic=is_italic)))
                start_index += len(text)
            elif kind == "NEWLINE":
                tokens.append(CarriageReturn(start_index, start_index + 1))
                start_index += 1
            elif kind == "LINK":
                text, url = [i for i in mo.groups() if i][1:]
                end_index = start_index + len(text)
                tokens.append(Link(start_index, end_index, text, url, TextStyle(underline=True)))
                start_index += len(text)
            elif kind == "UNORDERED_LIST_ITEM":
                text = [i for i in mo.groups() if i][1]
                end_index = start_index + len(text) + 2
                list_entry = ListItem(start_index, end_index, text)
                if not isinstance(tokens[-1], List):
                   list_token = List(start_index=start_index, end_index=end_index, list_id=list_id, ordered=False, items=[list_entry])
                   tokens.append(list_token)
                   list_id += 1
                else:
                    tokens[-1].items.append(list_entry)
                    tokens[-1].end_index = end_index
                start_index += len(text)
            else:
                continue
        return tokens

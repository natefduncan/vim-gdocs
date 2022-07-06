from typing import List as TList
from docs.tokens import Token, Text, TextStyle, CarriageReturn, Header, Link, List, ListItem, Tab
import re

class Parser:
    pass

class Google(Parser):
    def __init__(self, doc):
        self.doc = doc

    @staticmethod
    def generate_text(e: dict) -> TList[Token]:
        tokens = [] 
        cr = "\n" in e["textRun"]["content"]
        if cr:
            end_index = e["endIndex"]-1
            text = e["textRun"]["content"].replace("\n", "")
        else:
            text = e["textRun"]["content"]
            end_index = e["endIndex"]
        tokens.append(
                Text(
                    start_index=e["startIndex"], 
                    end_index=end_index, 
                    text=text,  
                    style=TextStyle(
                        e["textRun"]["textStyle"].get("bold", False), 
                        e["textRun"]["textStyle"].get("italic", False), 
                        e["textRun"]["textStyle"].get("underline", False)
                        )
                    ) 
                )
        if cr: 
            tokens.append(CarriageReturn(e["endIndex"]-1, e["endIndex"]))
        return tokens

    @staticmethod
    def generate_link(e: dict) -> TList[Token]:
        tokens = []
        start_index = e["startIndex"]
        end_index = e["endIndex"]
        text = e["textRun"]["content"]
        url = e["textRun"]["textStyle"]["link"]["url"]
        style=TextStyle(
                e["textRun"]["textStyle"].get("bold", False), 
                e["textRun"]["textStyle"].get("italic", False), 
                e["textRun"]["textStyle"].get("underline", False)
                )
        tokens.append(Link(start_index, end_index, text, url, style))
        return tokens

    def generate_list_item(self, paragraph, text_tokens) -> TList[Token]:
        tokens = []
        start_index = text_tokens[0].start_index 
        end_index = text_tokens[-1].end_index
        list_id = paragraph["paragraph"]["bullet"]["listId"]
        list_item = ListItem(start_index, end_index, text_tokens)
        list_token = next((i for i in self.tokens if isinstance(i, List) and i.list_id == list_id), None)
        if list_token:
            list_token.items.append(list_item)
            list_token.end_index = end_index
        else:
            ordered = self.doc["lists"][list_id]["listProperties"]["nestingLevels"][0].get("glyphType") != None
            list_token = List(start_index, end_index, list_id=list_id, ordered=ordered, items=[list_item])
            tokens.append(list_token)
        return tokens

    @staticmethod
    def generate_carriage_return(e: dict) -> TList[Token]:
        return [CarriageReturn(e["startIndex"], e["endIndex"])]

    @staticmethod
    def generate_tab(e) -> TList[Token]:
        return [Tab(e["startIndex"], e["endIndex"])]

    def parse_paragraph(self, paragraph) -> TList[Token]:
        tokens = []
        is_bullet = "bullet" in paragraph["paragraph"]
        for i in paragraph["paragraph"]["elements"]:
            if i["textRun"]["content"] == "\n":
                tokens += self.generate_carriage_return(i)
            elif "link" in i["textRun"]["textStyle"]:
                tokens += self.generate_link(i)
            else:
                tokens += self.generate_text(i)
        if is_bullet:
            tokens = self.generate_list_item(paragraph, tokens)
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
        self.token_re = "|".join(f'(?P<{name}>{regex})' for name, regex in self.token_spec)
 
    def parse_match(self, mo, start_index):
        kind = mo.lastgroup
        value = mo.group()
        tokens = []
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
        return start_index, tokens
    
    def _parse(self, text, start_index=1):
        tokens = []
        list_id = 0
        for mo in re.finditer(self.token_re, text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == "UNORDERED_LIST_ITEM":
                text = [i for i in mo.groups() if i][1]
                text += "\n"
                end_index, sub_tokens = self._parse(text, start_index)
                #  for t in sub_tokens:
                    #  t.start_index += 1
                    #  t.end_index += 1
                #  end_index += 1 
                #  sub_tokens.insert(0, Tab(sub_tokens[0].start_index-1, sub_tokens[0].start_index))
                list_entry = ListItem(start_index, end_index, sub_tokens)
                if not isinstance(tokens[-1], List):
                    list_token = List(start_index=start_index, end_index=end_index, list_id=list_id, ordered=False, items=[list_entry])
                    tokens.append(list_token)
                    list_id += 1
                else:
                    tokens[-1].items.append(list_entry)
                    tokens[-1].end_index = end_index
                start_index = end_index 
            else:
                start_index, sub_tokens = self.parse_match(mo, start_index)
                tokens += sub_tokens
        return start_index, tokens


    def parse(self):
        start_index, tokens = self._parse(self.text, 1)
        return tokens



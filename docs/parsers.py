from typing import List
from docs.tokens import Token, Text, TextStyle, CarriageReturn, Header, Link
import re

class Parser:
    pass

class Google(Parser):
    def __init__(self, doc):
        self.doc = doc

    def parse_paragraph(self, paragraph) -> List[Token]:
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

    def parse(self) -> List[Token]:
        content = self.doc.get("body").get("content")
        output = []
        for e in content:
            if 'paragraph' in e:
                output += self.parse_paragraph(e)
        return output

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
                ("LINK", r'(?:__|[*#])|\[(.*?)\]\((.*?)\)'), 
                ("NORMAL", r'.+')
        ]
 
    def parse(self):
        token_re = "|".join(f'(?P<{name}>{regex})' for name, regex in self.token_spec)
        start_index = 1
        tokens = []
        for mo in re.finditer(token_re, self.text):
            kind = mo.lastgroup
            value = mo.group()
            if kind in ["BOLD", "ITALIC", "BOLD_ITALIC", "NORMAL"]:
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
            else:
                continue
        return tokens

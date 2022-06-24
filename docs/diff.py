import difflib

def generate_delete(start_index, end_index):
    return {
            "deleteContentRange": {
                "range" : {
                    "endIndex": end_index, 
                    "startIndex": start_index + 1
                    }
                }
            }

def generate_insert(index, text):
    return {
            "insertText": {
                "location": {
                    "index": index + 1
                    }, 
                "text" : text.decode("utf-8")
                }
            }
 

def generate_batch_updates(starting_content, modified_content): 
    d = difflib.SequenceMatcher(a=starting_content, b=modified_content)
    batch = []
    for code in d.get_opcodes():
        tag, i1, i2, j1, j2 = code
        text = modified_content[j1:j2]
        if tag == "replace":
            batch.append(generate_delete(i1, i2))
            batch.append(generate_insert(i1, text))
        elif tag == "delete":
            batch.append(generate_delete(i1, i2))
        elif tag == "insert":
            batch.append(generate_insert(i1, text))
        elif tag == "equal":
            pass
    return batch 


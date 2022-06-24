import os
import json
import click
import sys, tempfile, os
from subprocess import call
from docs.ggl import get_docs_service, get_drive_service 
from docs.diff import generate_batch_updates

def create_temp_file(content):
    EDITOR = os.environ.get("EDITOR", "vim")
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write(content)
        tf.flush()
        call([EDITOR, tf.name])
        
        tf.seek(0)
        return tf.read()

def read_paragraph_element(element):
    text_run = element.get('textRun')
    if not text_run:
        return ''
    return text_run.get('content')


def read_structural_elements(elements):
    text = ''
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text += read_paragraph_element(elem)
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get('table')
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    text += read_structural_elements(cell.get('content'))
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_structural_elements(toc.get('content'))
    return text


@click.group()
def cli():
    pass

@click.command()
@click.option("--creds-path", "-C", default="creds/token.json")
@click.argument("name")
def open_file(creds_path, name):
    path = os.path.abspath(creds_path)
    drive = get_drive_service(path)
    docs = get_docs_service(path)
    # Search for file in drive
    files = drive.files().list(q=f"name contains '{name}'", includeItemsFromAllDrives=True, supportsAllDrives=True).execute()
    if files["files"]:
        file_id = files["files"][0]["id"]
        doc = docs.documents().get(documentId=file_id).execute()
        doc_content = doc.get('body').get('content')
        starting_content = read_structural_elements(doc_content)
        modified_content = create_temp_file(bytes(starting_content, "UTF-8"))
        batch_requests = generate_batch_updates(starting_content, modified_content)
        docs.documents().batchUpdate(documentId=file_id, body={"requests": batch_requests}).execute()

@click.command()
@click.option("--creds-path", "-C", default="creds/token.json")
@click.argument("doc-id")
def file(creds_path, doc_id):
    path = os.path.abspath(creds_path)
    docs = get_docs_service(path)
    click.echo(json.dumps(docs.documents().get(documentId=doc_id).execute()))
 
cli.add_command(open_file)
cli.add_command(file)

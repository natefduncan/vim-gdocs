import os
import json
import click
import sys, tempfile, os
from subprocess import call
from docs.ggl import get_docs_service, get_drive_service 
from docs.diff import generate_batch_updates
from docs import parsers, compilers

def create_temp_file(content):
    EDITOR = os.environ.get("EDITOR", "vim")
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write(content)
        tf.flush()
        call([EDITOR, tf.name])
        
        tf.seek(0)
        return tf.read()

@click.group()
def cli():
    pass

@click.command(name="open")
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
        tokens = parsers.Google(doc).parse()
        click.echo(tokens)
        compiled_doc = compilers.Markdown(tokens).compile()
        #  modified_content = create_temp_file(bytes(compiled_doc, "UTF-8"))
        tokens = parsers.Markdown(compiled_doc).parse()
        click.echo(tokens)
        #  batch_requests = generate_batch_updates(starting_content, modified_content.decode('utf-8'))
        #  print(batch_requests)
        #  docs.documents().batchUpdate(documentId=file_id, body={"requests": batch_requests}).execute()

@click.command(name="file")
@click.option("--creds-path", "-C", default="creds/token.json")
@click.argument("doc-id")
def file_info(creds_path, doc_id):
    path = os.path.abspath(creds_path)
    docs = get_docs_service(path)
    click.echo(json.dumps(docs.documents().get(documentId=doc_id).execute()))
 
cli.add_command(open_file)
cli.add_command(file_info)

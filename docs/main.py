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
        tokens_google = parsers.Google(doc).parse()
        compiled_markdown = compilers.Markdown(tokens_google).compile()
        modified_content = create_temp_file(bytes(compiled_markdown, "UTF-8"))
        tokens_markdown = parsers.Markdown(modified_content.decode("utf-8")).parse()
        compiled_google = compilers.Google(tokens_markdown).compile()
        compiled_google.insert(0, compilers.Google.generate_delete(1, tokens_google[-1].end_index-1))
        docs.documents().batchUpdate(documentId=file_id, body={"requests": compiled_google}).execute()

@click.command(name="file")
@click.option("--creds-path", "-C", default="creds/token.json")
@click.argument("doc-id")
def file_info(creds_path, doc_id):
    path = os.path.abspath(creds_path)
    docs = get_docs_service(path)
    click.echo(json.dumps(docs.documents().get(documentId=doc_id).execute()))
 
cli.add_command(open_file)
cli.add_command(file_info)

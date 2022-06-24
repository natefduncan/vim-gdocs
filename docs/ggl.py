import os 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"]

def get_creds(creds_path="creds/token.json"):
    creds = None
    if os.path.exists(creds_path):
        creds = Credentials.from_authorized_user_file(creds_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            directory = os.path.dirname(creds_path)
            flow = InstalledAppFlow.from_client_secrets_file(f"{directory}/credentials.json", SCOPES)
            print(flow.redirect_uri)
            creds = flow.run_local_server(open_browser=False)
            with open('creds/token.json', 'w') as token:
                token.write(creds.to_json())
    return creds

def get_drive_service(creds_path):
    creds = get_creds(creds_path)
    return build('drive', 'v3', credentials=creds, cache_discovery=False)  

def get_docs_service(creds_path):
    creds = get_creds(creds_path)
    return build("docs", "v1", credentials=creds, cache_discovery=False) 

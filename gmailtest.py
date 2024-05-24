import base64
import os

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.utils import formataddr

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.labels'
]
creds = None
token_path = '/tmp/test-gtoken.json'
if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'config/client_secret_720316148822-bfgvvbrhhjmulfr8bqtosms7jl57iap2.apps.googleusercontent.com.json',
            SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token_path, 'w') as token:
        token.write(creds.to_json())
service = build('gmail', 'v1', credentials=creds)

#
# msg = MIMEMultipart()
# msg['From'] = formataddr(('Kimmel Tamás', 'kumm0307@gmail.com'))
# msg['To'] = formataddr(('Kimmel Tamás', 'kumm0307@gmail.com'))
# msg['Date'] = formatdate(localtime=True)
# msg['Subject'] = "gmail api test"
# msg.attach(MIMEText("gmail api test"))
# # encoded message
# encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
# create_message = {'raw': encoded_message }
# send_message = (service.users().messages().send
#                 (userId="me", body=create_message).execute())
# print(F'Message Id: {send_message["id"]}')

service.users().labels().create(userId="me", body={
    'name': 'Test2',
}).execute()
print(service.users().labels().list(userId="me").execute())

import base64

from googleapiclient.discovery import build


class MailClient:
    def __init__(self, creds):
        self.service = build('gmail', 'v1', credentials=creds)

    def send(self, msg_bytes, label_ids=[]):
        encoded_message = base64.urlsafe_b64encode(msg_bytes).decode()
        create_message = {
            'raw': encoded_message,
            'labelIds': label_ids
        }
        messages = self.service.users().messages()
        return messages.send(userId="me", body=create_message).execute()

    def get_labels(self):
        return self.service.users().labels().list(userId="me").execute()

    def create_label(self, name):
        return self.service.users().labels().create(userId="me", body={
            'name': name,
        }).execute()

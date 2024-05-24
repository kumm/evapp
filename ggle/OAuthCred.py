import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class OAuthCred:
    def __init__(self, scopes, credentials_path, token_path=None):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.scopes = scopes
        self.creds = None

    def open(self, host='localhost', port=0, bind="127.0.0.1"):
        # with open(service_account_json_path) as source:
        #     info = json.load(source)
        # creds = service_account.Credentials.from_service_account_info(info)
        if self.token_path is not None and os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path)
        if not self.creds or (not self.creds.valid and not self.creds.expired):
            self.creds = self._oauth_flow(host, port, bind)
        return self.creds

    def _oauth_flow(self, host, port, bind):
        flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
        creds = flow.run_local_server(port=port, host=host, bind_addr=bind)
        if not creds.valid:
            raise RuntimeError('Failed oauth flow')
        return creds

    def close(self):
        if self.token_path is not None:
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
            os.chmod(self.token_path, 0o600)


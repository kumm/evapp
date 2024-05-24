from enum import Enum

__all__ = [
    'MailClient',
    'OAuthCred',
    'SpreadSheetClient',
    'SpreadSheet',
    'OAuthScopes'
]


class OAuthScopes(Enum):
    SHEETS_RW = 'https://www.googleapis.com/auth/spreadsheets'
    MAIL_SEND = 'https://www.googleapis.com/auth/gmail.send'
    MAIL_LABEL = 'https://www.googleapis.com/auth/gmail.labels'

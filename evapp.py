from __future__ import print_function

import argparse
import getpass
import glob
import os
from datetime import datetime, timedelta

import pytz

from commands.get_statements import get_statements, write_statements
from commands.get_wisebatch import get_wisebatch
from commands.mail_statements import mail_statements
from commands.send_money import send_money
from commands.sync_account import sync_account
from config import google_config, evapp_config, wise_config
from ggle import OAuthScopes
from ggle.MailClient import MailClient
from ggle.OAuthCred import OAuthCred
from ggle.SpreadSheet import SpreadSheet
from ggle.SpreadSheetClient import SpreadSheetClient
from wise.Account import Account
from wise.WiseClient import WiseClient

TZ = pytz.timezone("Europe/Budapest")

my_parser = argparse.ArgumentParser()
my_parser.add_argument('cmd', type=str, help='get-statememts/mail-statements/get-wisebatch/send-money/sync-account')
my_parser.add_argument('--target', type=str, help='Target dir', required=False,
                       default=evapp_config.download_path)
my_parser.add_argument('--year', type=int, help='Year', required=False,
                       default=(datetime.now() - timedelta(days=31)).year)
my_parser.add_argument('--month', type=int, help='Month', required=False,
                       default=(datetime.now() - timedelta(days=31)).month)
args = my_parser.parse_args()


def main():
    if args.cmd == 'sync-account':
        sync_account(get_spreadsheet(), get_latest_statements_zip(), TZ)

    if args.cmd == 'get-statements':
        statements = get_statements(get_account(), args.year, args.month)
        write_statements(args.target, statements)

    if args.cmd == 'mail-statements':
        mail_statements(
            gmail_client=get_gmail(),
            account=get_account(),
            to_addr=evapp_config.accountant_addr,
            from_addr=google_config.send_from,
            year=args.year,
            month=args.month
        )

    if args.cmd == 'get-wisebatch':
        get_wisebatch(get_spreadsheet(), args.target)

    if args.cmd == 'send-money':
        send_money(get_spreadsheet(), get_account())


def get_account():
    # Read the private key file as bytes.
    with open(wise_config.key_file, 'rb') as f:
        private_key_bytes = f.read()
    private_key_passphrase = getpass.getpass("Wise private key passphrase:")
    wise_client = WiseClient(
        private_key_bytes=private_key_bytes,
        private_key_passphrase=private_key_passphrase,
        token=wise_config.token
    )
    return Account(wise_client)


g_oauth = None


def get_google_creds():
    scopes = [OAuthScopes.MAIL_SEND.value, OAuthScopes.SHEETS_RW.value, OAuthScopes.MAIL_LABEL.value]
    global g_oauth
    g_oauth = OAuthCred(scopes, google_config.key_file, google_config.oauth_token_path)
    return g_oauth.open(host=google_config.oauth_redirect_host,
                        port=google_config.oauth_http_port,
                        bind=google_config.oauth_http_bind)


def get_spreadsheet():
    return SpreadSheet(google_config.spreadsheet_id, SpreadSheetClient(get_google_creds()))


def get_gmail():
    return MailClient(get_google_creds())

def get_latest_statements_zip(downloads_folder=None):
    if downloads_folder is None:
        downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')

    zip_files = glob.glob(os.path.join(downloads_folder, 'statement*.zip'))
    if not zip_files:
        raise FileNotFoundError("No statement ZIP files found in Downloads folder.")

    latest_zip = max(zip_files, key=os.path.getmtime)
    print(f"Latest ZIP file found: {latest_zip}")
    return latest_zip


if __name__ == '__main__':
    main()

if g_oauth is not None:
    g_oauth.close()

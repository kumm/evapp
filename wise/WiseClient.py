import base64
import json
from enum import Enum

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import urllib3
import sys
from urllib.parse import urlencode
from Crypto.Hash import SHA256


class StatementType(Enum):
    FLAT = 'FLAT'
    COMPACT = 'COMPACT'


class StatementFormat(Enum):
    PDF = 'pdf'
    CSV = 'csv'
    JSON = 'json'


class BalanceType(Enum):
    STANDARD = 'STANDARD'
    SAVINGS = 'SAVINGS'


class WiseClient:
    def __init__(
            self,
            private_key_bytes,
            token,
            private_key_passphrase=None,
            base_url='https://api.transferwise.com'
    ):
        # self.private_key = rsa.PrivateKey.load_pkcs1(private_key_data, 'PEM')
        self.private_key = RSA.import_key(private_key_bytes, private_key_passphrase)
        self.token = token
        self.http = urllib3.PoolManager()
        self.base_url = base_url

    def get_profiles(self):
        return self.sca_req_json('GET', '/v2/profiles')

    def get_multi_currency_account(self, profile_id):
        return self.sca_req_json('GET', f'/v4/profiles/{profile_id}/multi-currency-account')

    def get_recipient(self, account_id):
        return self.sca_req_json('GET', f'/v1/accounts/{account_id}')

    def create_quote(self, profile_id, source_currency, target_currency, target_account, source_amount, target_amount):
        return self.sca_req_json(
            'POST', f'/v3/profiles/{profile_id}/quotes',
            body={
                'sourceCurrency': source_currency,
                'targetCurrency': target_currency,
                'targetAmount': target_amount,
                'sourceAmount': source_amount,
                'targetAccount': target_account,
            }
        )

    def create_transfer(self, target_account, quote_uuid, customer_transaction_id, reference):
        return self.sca_req_json(
            'POST', f'/v1/transfers',
            body={
                'targetAccount': target_account,
                'quoteUuid': quote_uuid,
                'customerTransactionId': customer_transaction_id,
                'details': {
                    'reference': reference
                }
            }
        )

    def fund_transfer(self, profile_id, transfer_id):
        return self.sca_req_json(
            'POST', f'/v3/profiles/{profile_id}/transfers/{transfer_id}/payments',
            body={
                'type': 'BALANCE'
            }
        )

    def cancel_transfer(self, transfer_id):
        return self.sca_req_json('PUT', f'/v1/transfers/{transfer_id}/cancel')

    def get_balance_statement(self, profile_id, balance_id, interval_start, interval_end, balance_format, balance_type):
        return self.sca_req(
            'GET', f'/v1/profiles/{profile_id}/balance-statements/{balance_id}/statement.{balance_format.value}',
            query={
                'type': balance_type.value,
                'intervalStart': self.__convert_datetime(interval_start),
                'intervalEnd': self.__convert_datetime(interval_end),
                'addStamp': True,
                'statementLocale': 'hu'
            })

    @staticmethod
    def __convert_datetime(datetime):
        if datetime.tzinfo is None:
            datetime = datetime.astimezone()
        return datetime.isoformat().replace("+00:00", "Z")

    def get_statement(self, profile_id, account_id, currency, interval_start, interval_end, balance_format,
                      balance_type):
        return self.sca_req(
            'GET', f'/v3/profiles/{profile_id}/borderless-accounts/{account_id}/statement.{balance_format.value}',
            query={
                'currency': currency,
                'type': balance_type.value,
                'intervalStart': self.__convert_datetime(interval_start),
                'intervalEnd': self.__convert_datetime(interval_end),
                'statementLocale': 'hu'
            })

    def get_balances(self, profile_id, balance_types: list[BalanceType]):
        types=','.join([b.value for b in balance_types])
        return self.sca_req_json('GET', f'/v4/profiles/{profile_id}/balances?types={types}')

    def sca_req_json(self, method, url, query=None, body=None):
        return json.loads(self.sca_req(method, url, query, body))

    def sca_req(self, method, url, query=None, body=None):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }

        req_url = self.base_url + url
        if query is not None:
            req_url += "?" + urlencode(query)

        while True:
            r = self.http.request(method, req_url, headers=headers, body=json.dumps(body), retries=False)
            if r.status == 200 or r.status == 201:
                return r.data
            elif r.status == 403 and r.getheader('x-2fa-approval') is not None:
                one_time_token = r.getheader('x-2fa-approval')
                headers['x-2fa-approval'] = one_time_token
                headers['X-Signature'] = self.do_sca_challenge(one_time_token)
            else:
                print('failed: ', r.status)
                print(r.data)
                sys.exit(0)

    def do_sca_challenge(self, one_time_token):
        # Use the private key to sign the one-time-token that was returned
        # in the x-2fa-approval header of the HTTP 403.
        # signed_token = rsa.sign(
        #     one_time_token.encode('ascii'),
        #     self.private_key,
        #     'SHA-256')

        msg_hash = SHA256.new(one_time_token.encode('ascii'))
        signed_token = pkcs1_15.new(self.private_key).sign(msg_hash)
        # Encode the signed message as friendly base64 format for HTTP
        # headers.
        signature = base64.b64encode(signed_token).decode('ascii')

        return signature

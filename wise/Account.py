import json
import uuid
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from pprint import pprint

from wise.WiseClient import StatementType, BalanceType, WiseClient


class Account:
    def __init__(self, wise):
        self.wise = wise
        profiles = wise.get_profiles()
        self.profile_id = list(filter(lambda profile: profile['type'] == "BUSINESS", profiles))[0]['id']
        acc = wise.get_multi_currency_account(self.profile_id)
        self.account_id = acc['id']

    def transfer_prepare(self, target_account, target_amount, currency, reference):
        quote = self.wise.create_quote(profile_id=self.profile_id, source_currency=currency, target_currency=currency,
                                       target_account=target_account, target_amount=target_amount, source_amount=None)
        customer_transaction_id = uuid.uuid4()
        transfer = self.wise.create_transfer(target_account, quote['id'], str(customer_transaction_id), reference)
        recipient = self.wise.get_recipient(transfer['targetAccount'])
        return PreparedTransfer(
            account_number=recipient['details']['accountNumber'],
            sort_code=recipient['details']['sortCode'],
            account_holder_name=recipient['accountHolderName'],
            target_value=transfer['targetValue'],
            transfer_id=transfer['id']
        )

    def transfer_perform(self, transfer_id):
        self.wise.fund_transfer(self.profile_id, transfer_id)

    def transfer_cancel(self, transfer_id):
        self.wise.cancel_transfer(transfer_id)

    def download_statement(self, currency, start_date, end_date, format, type):
        return self.wise.get_statement(self.profile_id, self.account_id, currency, start_date, end_date, format, type)

    def get_balances(self, balance_type=BalanceType.STANDARD):
        balances = []
        for balance_dict in self.wise.get_balances(self.profile_id, balance_type):
            balances.append(Balance(self.profile_id, self.wise, balance_dict))
        return balances


class Balance:
    def __init__(self, profile_id, client: WiseClient, data):
        self.profile_id = profile_id
        self.client = client
        self.id = data['id']
        self.currency = data['currency']

    def download_statement(self, start_date, end_date, statement_format, statement_type):
        return self.client.get_balance_statement(self.profile_id, self.id, start_date, end_date,
                                                 statement_format,
                                                 statement_type)


@dataclass
class PreparedTransfer:
    account_number: str
    sort_code: str
    account_holder_name: str
    target_value: float
    transfer_id: int

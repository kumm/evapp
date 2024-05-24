import json
import uuid
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

from wise.WiseClient import WiseClient

token = '3d920bb0-c01a-4c21-b137-b0b6141bae88'  # Set API token from env
private_key_path = '/home/kumm/Workspace/Projects/evapp/id_rsa.pem'  # Change to private key path
wise = WiseClient(private_key_path, token)
profile_id = list(filter(lambda profile: profile['type'] == "BUSINESS", wise.get_profiles()))[0]['id']
account_id = wise.get_multi_currency_account(profile_id)['id']
currencies = ['EUR', 'HUF']

year = (datetime.now() - timedelta(days=31)).year
month = (datetime.now() - timedelta(days=31)).month

# target_path = f'/home/kumm/Documents/papir/ev/{year}-{month:02d}'
target_path = '.'


# if os.getenv('API_TOKEN') is None:
#     print('panic: no api token, please set with $ export API_TOKEN=xxx')
#     sys.exit(0)
# elif profile_id == '' or account_id == '':
#     print('panic: profile / account ID missing, please add them')
#     sys.exit(0)
# elif os.path.exists(private_key_path) is False:
#     print('panic: private key file not found, please update key path')
#     sys.exit(0)


def download_monthly_accountant_statement(currency, month, format='pdf'):
    start_date = datetime.now(timezone.utc).replace(year=year, month=month, day=1, hour=0, minute=0, second=0,
                                                    microsecond=0)
    next_month = start_date.replace(day=28) + timedelta(days=4)
    end_date = (next_month - timedelta(days=next_month.day)).replace(hour=23, minute=59, second=59, microsecond=999999)
    return wise.get_statement(profile_id, account_id, currency, start_date, end_date, format, 'FLAT')


def sum_statement_fees(currencies):
    sum_by_currency = {}
    for currency in currencies:
        statement_json = download_monthly_accountant_statement(currency, month, format='json')
        statement = json.loads(statement_json)
        for trx in statement['transactions']:
            if "totalFees" in trx:
                sum_fee(sum_by_currency, trx["totalFees"])
            if "fee" in trx["details"]:
                sum_fee(sum_by_currency, trx["details"]["fee"])
    return sum_by_currency


def sum_fee(sum_by_currency, fee_dict):
    v = sum_by_currency.setdefault(fee_dict["currency"], 0.0)
    sum_by_currency[fee_dict["currency"]] = v + fee_dict["value"]


def download_statements():
    for currency in currencies:
        target = f'{target_path}/{year}-{month:02d}_{currency}'
        with open(f'{target}.pdf', 'wb') as f:
            f.write(download_monthly_accountant_statement(currency, month, 'pdf'))
        with open(f'{target}.csv', 'wb') as f:
            f.write(download_monthly_accountant_statement(currency, month, 'csv'))


def transfer_prepare(target_account, target_amount, currency, reference):
    quote = wise.create_quote(profile_id=profile_id, source_currency=currency, target_currency=currency,
                              target_account=target_account, target_amount=target_amount, source_amount=None)
    customer_transaction_id = uuid.uuid4()
    transfer = wise.create_transfer(target_account, quote['id'], str(customer_transaction_id), reference)
    recipient = wise.get_recipient(transfer['targetAccount'])
    return PreparedTransfer(
        account_number=recipient['details']['accountNumber'],
        sort_code=recipient['details']['sortCode'],
        account_holder_name=recipient['accountHolderName'],
        target_value=transfer['targetValue'],
        transfer_id=transfer['id']
    )


def transfer_perform(transfer_id):
    wise.fund_transfer(profile_id, transfer_id)


def transfer_cancel(transfer_id):
    wise.cancel_transfer(transfer_id)

@dataclass
class PreparedTransfer:
    account_number: str
    sort_code: str
    account_holder_name: str
    target_value: float
    transfer_id: int


def main():
    download_statements()
    # print(f"Wise fees for {year}-{month:02d}:")
    # fee_sum = sum_statement_fees(currencies)
    # for i in fee_sum:
    #     print(f'{fee_sum[i]:.2f} {i}')

    # print(wise.get_recipient(308357167))
    # quote = wise.create_quote(profile_id=profile_id, source_currency='HUF', target_currency='HUF',
    #                           target_account=308357167, target_amount=1000, source_amount=None)
    # print(quote)
    # customer_transaction_id = uuid.uuid4()
    # transfer = wise.create_transfer(308357167, quote['id'], str(customer_transaction_id), 'test')
    #
    # print(transfer)
    ## wise.fund_transfer(profile_id, transfer['id'])

    # statement = get_statement("EUR", format='pdf')
    # print(statement)
    # if statement is not None and 'currency' in statement['request']:
    #     currency = statement['request']['currency']
    # else:
    #     print('something is wrong')
    #     sys.exit(0)
    #
    # if 'transactions' in statement:
    #     txns = len(statement['transactions'])
    # else:
    #     print('Empty statement')
    #     sys.exit(0)
    #
    # print('\n', currency, 'statement received with', txns, 'transactions.')


if __name__ == '__main__':
    main()

import json
import re
from datetime import datetime, timedelta
import dateutil.parser as dateparser
from dateutil.parser import ParserError
from ggle.SpreadSheet import SpreadSheet
from wise.Account import Account
from wise.WiseClient import StatementFormat, StatementType

TRX_TABLE_WIDTH = 24


def sync_account(spreadsheet: SpreadSheet, account: Account, tz):
    trx_cell_values = spreadsheet.get_trx_values()
    last_time, last_formulas = __find_last_trx_info(trx_cell_values, tz)
    balance_rows, new_trx_rows = __load_balance_statements(account, last_time, tz)
    __extend_trx_formulas(last_formulas, new_trx_rows)
    if len(new_trx_rows) > 0:
        spreadsheet.append_trx_values(len(trx_cell_values), new_trx_rows)
        spreadsheet.update_balance(balance_rows)


def __extend_trx_formulas(last_formulas, new_trx_rows):
    for row in new_trx_rows:
        last_formulas = [
            re.sub(r"([A-Z]+)([0-9]+)", lambda match: match.group(1) + str(int(match.group(2)) + 1), formula)
            for formula in last_formulas
        ]
        row.extend('' for x in range(len(row), TRX_TABLE_WIDTH))
        row.extend(last_formulas)


def __load_balance_statements(account, last_time, tz):
    new_trx_entries = []
    balance_rows = []
    for balance in account.get_balances():
        statement_json = balance.download_statement(last_time, datetime.now(), StatementFormat.JSON,
                                                    StatementType.FLAT)
        statement = json.loads(statement_json)
        balance_rows.append(__map_balance_row(statement['endOfStatementBalance']))
        for trx in statement['transactions']:
            new_trx_entries.append(__map_trx_entry(trx, tz))

    new_trx_entries.sort(key=lambda e: e[0])
    balance_rows.sort(key=lambda r: r[0])
    return balance_rows, [e[1] for e in new_trx_entries]


def __map_trx_entry(trx, tz):
    date = dateparser.isoparse(trx['date']).astimezone(tz)
    row = [
        date.strftime("%Y-%m-%d %H:%M:%S"),
        trx['referenceNumber'],
        trx['type'],
        trx['details']['type'],
        trx['amount']['value'],
        trx['amount']['currency'],
        trx['details'].get('recipient', {}).get('bankAccount', ''),
        trx['details'].get('recipient', {}).get('name', ''),
        trx['details'].get('senderAccount', ''),
        trx['details'].get('senderName', ''),
        trx['details'].get('paymentReference'),
        trx['details'].get('merchant', {}).get('name'),
        trx['details'].get('merchant', {}).get('city'),
        trx['details'].get('rate'),
        trx['details'].get('amount', {}).get('value', ''),
        trx['details'].get('amount', {}).get('currency', ''),
        trx['details'].get('sourceAmount', {}).get('currency'),
        trx['details'].get('targetAmount', {}).get('currency'),
        trx['details']['description'],
        json.dumps(trx),
    ]
    return date, row


def __map_balance_row(balance_result):
    return [
        balance_result['currency'], balance_result['value']
    ]


def __find_last_trx_info(trx_cell_values, tz):
    last_time = datetime.utcnow() - timedelta(days=31)
    last_formulas = []
    for trx in reversed(trx_cell_values):
        if len(trx) > 0 and trx[0] != '':
            try:
                last_time = tz.localize(dateparser.parse(trx[0])) + timedelta(seconds=1)
                last_formulas = [trx[c] for c in range(TRX_TABLE_WIDTH, len(trx))]
                break
            except ParserError:
                continue
            except OverflowError:
                continue

    return last_time, last_formulas

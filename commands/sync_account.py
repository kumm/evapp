import re
import re
import zipfile
from datetime import timedelta

import dateutil.parser as dateparser
from dateutil.parser import ParserError

from ggle.SpreadSheet import SpreadSheet
from wise.CamtXmlParser import CamtXmlParser

TRX_TABLE_WIDTH = 10


def sync_account(spreadsheet: SpreadSheet, zip_path, tz):
    trx_cell_values = spreadsheet.get_trx_values()
    last_time, last_formulas = __find_last_trx_info(trx_cell_values, tz)
    balance_rows, new_trx_rows = __load_balance_statements(zip_path, last_time, tz)
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


def __load_balance_statements(zip_path, last_time, tz):
    new_trx_entries = []
    balance_map = {}

    with zipfile.ZipFile(zip_path, 'r') as z:
        for file_info in z.infolist():
            if file_info.filename.endswith('.xml'):
                with z.open(file_info) as xml_file:
                    xml_data = xml_file.read()
                    camt = CamtXmlParser(xml_data, tz)
                    for trx in camt.parse_transactions():
                        if last_time is None or trx['ts'] > last_time:
                            new_trx_entries.append(__map_trx_entry(trx, tz))
                    amt, ccy = camt.parse_balance()
                    balance_map[ccy] = balance_map.get(ccy, 0) + float(amt)

    new_trx_entries.sort(key=lambda e: e[0])
    balance_rows = [[c, v] for c, v in balance_map.items()]
    balance_rows.sort(key=lambda r: r[0])
    return balance_rows, new_trx_entries


def __map_trx_entry(trx, tz):
    row = [
        trx['ts'].strftime("%Y-%m-%d %H:%M:%S"),
        trx['id'],
        trx['amt'].replace(".",","),
        trx['ccy'],
        trx['pty'],
        trx['ref'],
        trx['inf'],
        # trx['xml']
    ]
    return row


def __find_last_trx_info(trx_cell_values, tz):
    last_time = None
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

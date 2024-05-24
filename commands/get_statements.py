from datetime import datetime, timedelta

from wise.WiseClient import StatementFormat, StatementType


def get_statements(account, year, month):
    start_date, end_date = __get_month_date_interval(year, month)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = (end_date - timedelta(microseconds=1)).strftime('%Y-%m-%d')
    statements = {}
    for balance in account.get_balances():
        basename = f'statement_{balance.id}_{balance.currency}_{start_date_str}_{end_date_str}'
        statements[f'{basename}.pdf'] = \
            balance.download_statement(start_date, end_date, StatementFormat.PDF, StatementType.FLAT)
        statements[f'{basename}.csv'] = \
            balance.download_statement(start_date, end_date, StatementFormat.CSV, StatementType.COMPACT)
    return statements


def write_statements(target_path, statements):
    for name in statements:
        with open(f'{target_path}/{name}', 'wb') as f:
            f.write(statements[name])


def __get_month_date_interval(year, month):
    start_date = datetime.now().replace(year=year, month=month, day=1, hour=0, minute=0, second=0,
                                        microsecond=0)
    next_month = start_date.replace(day=28) + timedelta(days=4)
    end_date = next_month.replace(day=1)
    return start_date, end_date

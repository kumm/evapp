from ggle.SpreadSheetClient import ValueRenderOption, DateTimeRenderOption, InsertDataOption, ValueInputOption


class SpreadSheet:
    def __init__(self, spreadsheet_id, spreadsheet_client):
        self.client = spreadsheet_client
        self.spreadsheet_id = spreadsheet_id

    def __get_values(self, range,
                     valueRender=ValueRenderOption.UNFORMATTED_VALUE,
                     dateTimeRender=DateTimeRenderOption.FORMATTED_STRING):
        return self.client.get_values(self.spreadsheet_id, range, valueRender, dateTimeRender)

    def __get_spreadsheet(self):
        return self.client.get_spreadsheet(self.spreadsheet_id)

    def __append_values(self, range, value_input_option, values):
        return self.client.append_values(self.spreadsheet_id, range, value_input_option, InsertDataOption.INSERT_ROWS, {
            'range': range,
            'values': values
        })

    def __batch_update_values(self, range, value_input_option, values):
        return self.client.batch_update_values(self.spreadsheet_id, {
            'valueInputOption': value_input_option.value,
            'data': [
                {
                    'range': range,
                    'values': values,
                }
            ]
        })

    def get_trx_values(self):
        return self.__get_values("trx", ValueRenderOption.FORMULA)

    def get_wisebatch_values(self):
        return self.__get_values("wisebatch", ValueRenderOption.UNFORMATTED_VALUE)

    def append_trx_values(self, row_ndx_start, rows):
        return self.__append_values(f'trx!A{row_ndx_start + 1}:ZZ{row_ndx_start + len(rows) + 1}',
                                    ValueInputOption.USER_ENTERED, rows)

    def update_balance(self, rows):
        return self.__batch_update_values(f'balance!A2:B{len(rows) + 2}', ValueInputOption.USER_ENTERED, rows)

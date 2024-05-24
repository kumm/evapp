import json
import os
from enum import Enum

from googleapiclient.discovery import build


class ValueRenderOption(Enum):
    UNFORMATTED_VALUE = 'UNFORMATTED_VALUE'
    FORMATTED_VALUE = 'FORMATTED_VALUE'
    FORMULA = 'FORMULA'


class DateTimeRenderOption(Enum):
    SERIAL_NUMBER = 'SERIAL_NUMBER'
    FORMATTED_STRING = 'FORMATTED_STRING'


class ValueInputOption(Enum):
    RAW = 'RAW'
    USER_ENTERED = 'USER_ENTERED'


class InsertDataOption(Enum):
    OVERWRITE = 'OVERWRITE'
    INSERT_ROWS = 'INSERT_ROWS'


class SpreadSheetClient:
    def __init__(self, creds):
        service = build('sheets', 'v4', credentials=creds)
        self.sheet = service.spreadsheets()

    def get_values(self, spreadsheet_id, range,
                   valueRender=ValueRenderOption.UNFORMATTED_VALUE,
                   dateTimeRender=DateTimeRenderOption.FORMATTED_STRING):
        result = self.sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range,
            valueRenderOption=valueRender.value,
            dateTimeRenderOption=dateTimeRender.value
        ).execute()
        return result.get('values', [])

    def get_spreadsheet(self, spreadsheet_id):
        result = self.sheet.get(spreadsheetId=spreadsheet_id).execute()
        return result

    def append_values(self, spreadsheet_id, range, value_input_option, insert_data_option, value_range_body):
        return self.sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=range,
            valueInputOption=value_input_option.value,
            insertDataOption=insert_data_option.value,
            body=value_range_body
        ).execute()

    def batch_update_values(self, spreadsheet_id, body):
        return self.sheet.values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()

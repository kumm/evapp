def send_money(spreadsheet, account):
    transfers = []
    values = spreadsheet.get_wisebatch_values()
    values.pop(0)
    for row in values:
        target_amount = row[7]
        target_account = row[0]
        reference = row[8]
        if int(target_amount) > 0:
            transfer = account.transfer_prepare(target_account, target_amount, 'HUF', reference)
            transfers.append(transfer.transfer_id)
            print(transfer.sort_code, transfer.account_number, transfer.account_holder_name,
                  transfer.target_value + 'Ft', sep='\t')

    sure = input("Are you sure? (y/n): ").lower().strip()[:1] == "y"
    for transfer_id in transfers:
        if sure:
            print("no way")
            # account.transfer_perform(transfer_id)
        else:
            account.transfer_cancel(transfer_id)


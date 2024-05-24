import csv


def get_wisebatch(spreadsheet, target_path):
    values = spreadsheet.get_wisebatch_values()
    cols = len(values[0])
    with open(target_path + '/wisebatch.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        for row in values:
            for i in range(len(row), cols):
                row.append("")
            writer.writerow(row)

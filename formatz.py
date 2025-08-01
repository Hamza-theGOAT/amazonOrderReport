from openpyxl.utils import get_column_letter as getColLetters
from openpyxl.styles import Alignment
from openpyxl.worksheet.table import Table
from openpyxl import load_workbook

# Validate range params and pick max if not given


def getRange(ws, r0, r1, c0, c1):
    r0 = r0 if r0 is not None else ws.min_row
    r1 = r1 if r1 is not None else ws.max_row
    c0 = c0 if c0 is not None else ws.min_col
    c1 = c1 if c1 is not None else ws.max_col

    return r0, r1, c0, c1

# Selecting range (replicating Alt+A in excel)


def AltA(ws):
    r1 = ws.max_row
    c1 = ws.max_column

    return f"A1:{getColLetters(c1)}{r1}"

# Setting column width to max data length within the col (replicating Alt+HOI in excel)


def AltHOI(ws):
    colWidths = {}
    for row in ws.iter_rows():
        for cell in row:
            if cell.value:
                # Calculate the maximum length of each col
                colWidths[cell.column_letter] = max(
                    (colWidths.get(cell.column_letter, 0)),
                    len(str(cell.value))
                )
    # Add a little extra width
    for col, width in colWidths.items():
        ws.column_dimensions[col].width = width + 3


# Standard formatted table (for all sheets)
def tableFormatting(wb):
    for sh in wb.sheetnames:
        ws = wb[sh]
        ws.freeze_panes = 'A2'
        for col in ws.iter_cols(max_row=1, max_col=ws.max_column):
            for cell in col:
                cell.alignment = Alignment(horizontal='left')
        ws.sheet_view.showGridLines = False
        wsData = AltA(ws)
        ws.add_table(Table(displayName=f'{sh}', ref=wsData))
        ws = AltHOI(ws)


# Loading workbook to apply basic formats
def formatWB(wbNin, wbNout):
    wb = load_workbook(wbNin)
    tableFormatting(wb)
    wb.save(wbNout)


if __name__ == '__main__':
    wbNin = 'fileInput.xlsx'
    wbNout = 'fileOutput.xlsx'
    formatWB(wbNin, wbNout)

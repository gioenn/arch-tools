import pandas
from pathlib import Path
from pyexcelerate import Workbook

EXTENSION = ".RESULTS"

files = Path('.').glob(f'*{EXTENSION}')
files = sorted([str(x) for x in files])
#writer = pandas.ExcelWriter('RESULT.xlsx', engine=None)
wb = Workbook()
for f in files:
    print('Reading file', f)
    sheetName = f.split(EXTENSION)[0]
    df = pandas.read_csv(f, sep='\t', lineterminator='\n')
    print('Creating sheet', sheetName)
    wb.new_sheet(sheetName, data=[df.columns] + list(df.values))
    
print('Writing result on disk (it may take a bunch of minutes...)')
wb.save('RESULT.xlsx')
import pandas as pd
from pathlib import Path
import re
from io import StringIO


def genParams(files, indexes, df1, df2):
    def parseName(index):
        index = index.replace("_CASE1", "") # support for initial naming
        parts = index.split('_CONTROL')
        case = int(parts[-1])
        sheet = "_".join(parts[0].split("_")[1:])
        return case, sheet
    
    permutations = pd.ExcelFile('permutations.xlsx')
    sheets = {}
    for i in indexes:
        case, sheet = parseName(i)
        if sheet not in sheets:
            sheetdf = pd.read_excel(permutations, sheet)
            sheets[sheet] = sheetdf
        else:
            sheetdf = sheets[sheet]
        for c in PERM1:
            df1.at[i,c] = sheetdf.at[case-1, c]

        


def genDfFromCols(files, indexes, df, columns, reduce=lambda cv: cv.sum()):
    for i, f in zip(indexes, files):
        print('Analyzing', f)    
        with open(f, mode='r', newline='') as fIn:
            data = fIn.readlines()
            data = [re.sub("\s+", ",", s.strip()) for s in data]
            data = StringIO('\n'.join(data))
            dfIn = pd.read_csv(data)
            for c in columns:
                df.at[i,c] = reduce(dfIn[c])

def analyzeResults(files, indexes, df1, df2):
    genDfFromCols(files, indexes, df1, C_RESULTS1, reduce=lambda cv: cv.sum()/3600)
    for i, f in enumerate(indexes):
        df2.at[f, C_RESULTS2[0]] = df1.iloc[i, 9:12].sum()
        df2.at[f, C_RESULTS2[1]] = df1.iloc[i, 12:-2].sum()
    
def analyzeHp(files, indexes, df1, df2):
    genDfFromCols(files, indexes, df1, C_HPS1)    


# CONSTANTS AND TOOLS

EXTS = ['RESULTS', 'HP', '']
C_RESULTS1 = ["Q_BUI_H", "Q_BUI_C", "Q_BUI_DHW", "Q_BUI_TOT", "WEL_SFC_H", "WEL_SFC_C", "WEL_DHW", "WEL_PUMP_GEN", "WEL_PUMP_ST", "WEL_PUMP_HP1", "WEL_PUMP_HP2", "WEL_HP1_H", "WEL_HP1_C", "WEL_HP_H", "WEL_HP_C"]
C_RESULTS2 = ["Q_BUI_TOT", "WEL_TOT"]
C_HPS1 = ["COP_HP1", "COP_HP2"]
PERM1 = ["A_UP", "B_LOW", "dt_AB", "V_MIX_TSP", "dT_CD", "A", "B", "C", "D"]
C_ALL1 = PERM1 + C_RESULTS1 + C_HPS1 
C_ALL2 = C_RESULTS2

FUNCS = [analyzeResults, analyzeHp, genParams]

def main():
    files = []
    indexes = None
    for i, ext in enumerate(EXTS): 
        if not ext:
            files.append([])
            continue
        fs = Path('.').glob(f'*.{ext}')
        if not fs:
            print(f"Missing {ext} files in folder")
        fs = sorted([str(x) for x in fs])
        iz = ['.'.join(x.split('.')[0:-1]) for x in fs] 
        if indexes and iz != indexes:
            print(f'{ext} and {exts[i-1]} files do not match')
            return
        files.append(fs)
        indexes = iz

    print('Files ok...')
    print('Starting analysis...') 
       
    writer = pd.ExcelWriter('ALL_ANALYSIS.xlsx', engine='xlsxwriter')

    df1 = pd.DataFrame(columns=C_ALL1, index=indexes)
    df2 = pd.DataFrame(columns=C_ALL2, index=indexes)
    
    for fun, fs in zip(FUNCS, files):
        fun(fs, indexes, df1, df2)
    
    print('Generating ALL_ANALYSIS file...')    
    df1.to_excel(writer, sheet_name=f'Sheet 1')
    df2.to_excel(writer, sheet_name=f'Sheet 2')
    writer.save()
    print('Done')    


    
main()
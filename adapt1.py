import pandas as pd
import sys
import os

def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1
    return path

path = input('Insert input excel file: ')
T_ON_IS = int(input('Insert T_ON_IS (as number of time steps): '))
C_EL_CUT_IN = float(input('Insert C_EL_CUT_IN: '))
LOOK_AHEAD = int(input('Insert LOOK AHEAD (as number of time steps): '))
NOISE = 0

df = pd.read_excel(path, engine='openpyxl')

f = open(uniquify(f'{path.split(".")[0]}.txt'), 'w')
f.write(f'file={path} T_ON_IS={T_ON_IS} C_EL_CUT_IN={C_EL_CUT_IN} NOISE={NOISE} LOOK_AHEAD={LOOK_AHEAD}\n')


for index, row in df.iterrows():
    if not index:
        continue
    PRD_ST_ON = 0
    for pIndex in range(index+1, index+(LOOK_AHEAD-T_ON_IS)+2):
        print(df.iloc[pIndex:pIndex+T_ON_IS])
        cond1 = [pRow[5] > C_EL_CUT_IN for pRow in df.iloc[pIndex:pIndex+T_ON_IS].itertuples()]
        if len(cond1) == T_ON_IS and all(cond1):
            PRD_ST_ON = 1
            break
    f.write(f'{round(row[0],1)}\t{PRD_ST_ON}\n')

f.write(f'{round(row[0],1)}\t{PRD_ST_ON}\n')
f.close()


    
        
        
        
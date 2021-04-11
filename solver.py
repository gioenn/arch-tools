from numpy import arange
import csv
import sys

# UTILS
def fix(parameter, *values):
    parameter.clear()
    for value in values:
        parameter.append(float(value))

def init(min, max, step):
    return arange(min, max+0.5, step).tolist()

# TEMPERATURE SEARCH STEP
step = 1

# CONSTANTS
Tmin_SFC = 15
Tmax_SFC = 35
dt_HX = 3
max_A_UP = 22
min_B_LOW = 27
min_HYS = 0

# SEARCH RANGES (min, max, step). both min and max included
A_UPs = init(Tmin_SFC, max_A_UP, step)
B_LOWs = init(min_B_LOW, Tmax_SFC, step)
dT_ABs = init(0, Tmax_SFC, step)
V_MIX_TSPs = init(Tmin_SFC, Tmax_SFC, step)
dT_CDs = init(0, Tmax_SFC, step)
dband_CDs = init(0, Tmax_SFC, step) 

# FIX
# Example: fix(V_MIX_TSPs, 25.0) fixes the value of V_MIX_TSP to 25 degrees
fix(A_UPs, 20.0)
fix(B_LOWs, 27.0)
fix(dT_ABs, 2.0)
fix(V_MIX_TSPs, 32.0)
fix(dT_CDs, 1.0)



# CONSTRAINTS
def C0(A_UP, B_LOW, dT_AB, V_MIX_TSP, dT_CD, dband_CD): return dT_AB > 0
def C1(A_UP, B_LOW, dT_AB, V_MIX_TSP, dT_CD, dband_CD): return A_UP >= Tmin_SFC+dt_HX+dT_AB
def C2(A_UP, B_LOW, dT_AB, V_MIX_TSP, dT_CD, dband_CD): return B_LOW  <= Tmax_SFC-dt_HX-dT_AB
def C3(A_UP, B_LOW, dT_AB, V_MIX_TSP, dT_CD, dband_CD): return A_UP - B_LOW < dT_AB
def C4(A_UP, B_LOW, dT_AB, V_MIX_TSP, dT_CD, dband_CD): return dT_CD > 0
def C5(A_UP, B_LOW, dT_AB, V_MIX_TSP, dT_CD, dband_CD): return dband_CD >= 0
def C6(A_UP, B_LOW, dT_AB, V_MIX_TSP, dT_CD, dband_CD): return V_MIX_TSP - dT_CD > Tmin_SFC + dband_CD
def C7(A_UP, B_LOW, dT_AB, V_MIX_TSP, dT_CD, dband_CD): return V_MIX_TSP + dT_CD < Tmax_SFC - dband_CD
# make sure hysteris A and B are wider than min_HYS
def C8(A_UP, B_LOW, dT_AB, V_MIX_TSP, dT_CD, dband_CD): return B_LOW-(A_UP-dT_AB) >= min_HYS and B_LOW+dT_AB-A_UP >= min_HYS 
# make sure hysteris C and D are wider than min_HYS
def C9(A_UP, B_LOW, dT_AB, V_MIX_TSP, dT_CD, dband_CD): return (V_MIX_TSP-dT_CD)-(Tmin_SFC+dband_CD) >= min_HYS and (Tmax_SFC-dband_CD)-(V_MIX_TSP+dT_CD) >= min_HYS 


# SEARCH ALGORITHM

CONSTRAINTS = [C0, C1, C2, C3, C4, C5, C6, C7, C8, C9]

solutions = []
hystereses = set()

n_format = "%d" if isinstance(step, int) or step.is_integer() else "%.1f"
h_format = "%s-%s" % (n_format, n_format)

for A_UP in A_UPs:
    for B_LOW in B_LOWs:
        for dT_AB in dT_ABs:
            for V_MIX_TSP in V_MIX_TSPs:
                for dT_CD in dT_CDs:
                    for dband_CD in dband_CDs:
                        candidate = (A_UP, B_LOW, dT_AB, V_MIX_TSP, dT_CD, dband_CD)
                        if all([CONSTRAINT(*candidate) for CONSTRAINT in CONSTRAINTS]):
                            A = h_format % (A_UP-dT_AB, B_LOW)
                            B = h_format % (B_LOW+dT_AB, A_UP)
                            C = h_format % (Tmin_SFC+dband_CD, V_MIX_TSP-dT_CD)
                            D = h_format % (Tmax_SFC-dband_CD, V_MIX_TSP+dT_CD)
                            hysteresis = (A, B, C, D)
                            if hysteresis not in hystereses:
                                solutions.append(candidate + hysteresis)
                                hystereses.add(hysteresis)


# FILE CREATION


filename = (sys.argv[1] if len(sys.argv) > 1 else 'data') + '.csv'

with open(filename, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(["A_UP", "B_LOW", "dt_AB", "V_MIX_TSP", "dT_CD", "dband_CD", "A", "B", "C", "D"])
    writer.writerows(solutions)

print("solution count: ", len(solutions))

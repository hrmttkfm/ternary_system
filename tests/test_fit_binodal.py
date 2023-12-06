import numpy as np
import pandas as pd
import sys
sys.path.append(r"src")
import pandas as pd
import numpy as np 
from ternary_diagram import Ternary, default_colors, default_markers
from ternary_data import TernaryData

if __name__ == "__main__":
    tr = Ternary("Psf+TEG", "NMP", "H2O")

    df = pd.read_excel(r"tests\experiment_data_XSA.xlsx").dropna()
    for tp, c, m in zip(df.groupby(["備考", "温度"]), default_colors, default_markers):
        idx, sdf = tp
        tr.scatter(sdf["ポリマー"]+sdf["添加剤"], sdf["良溶媒"], sdf["貧溶媒"], str(idx[0]) + " " + str(idx[1]) + "℃", c, m)
    tb = TernaryData(df["ポリマー"]+df["添加剤"], df["良溶媒"], df["貧溶媒"], str(idx[1]))
    tb.fitData(deg = 1)
    tb.exportFitFunc(r"tests\binodalFitFunc.pkl")

    polymer = np.linspace(0, 1, 100)
    solvent = tb.PSFitFunc(polymer)
    non_solvent = 1. - polymer - solvent
    tr.lines(polymer, solvent, non_solvent, "フィッティング", "red", )
    tr.saveHTML(r"tests\fit_binodal.html")
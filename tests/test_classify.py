"""
液組成をバイノーダル曲線の内側か外側かを判定するプログラムをテスト
"""
import numpy as np
import pandas as pd
import sys
sys.path.append(r"src")
from ternary_diagram import Ternary, default_colors, default_markers
from ternary_data import TernaryData

if __name__ == "__main__":
    data = pd.read_excel(r"tests\random_fraction.xlsx")
    td = TernaryData()
    td.loadFitFunc(r"tests\binodalFitFunc.pkl")

    tr = Ternary("Psf+TEG", "NMP", "H2O")


    polymer = np.linspace(0, 1., 100)
    solvent = td.fitFunc(polymer)
    non_solvent = 1. - polymer - solvent
    tr.lines(polymer, solvent, non_solvent, "フィッティング", "red")

    for idx, row in data.iterrows():
        if td.isSeparate(row["ポリマー"], row["良溶媒"], row["貧溶媒"]):
            color = "#19D3F3"
        else:
            color = "#B6E880"
        tr.scatter([row["ポリマー"]], [row["良溶媒"]], [row["貧溶媒"]], "", color)

    tr.saveHTML(r"tests\test_classify.html")
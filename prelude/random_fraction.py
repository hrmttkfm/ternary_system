# ランダムな3成分組成を作り出し, 結果をtestに格納する
import random
import pandas as pd

if __name__ == "__main__":
    values = []
    for i in range(300):
        x = random.random()
        y = 1
        while x + y > 1.:
            y = random.random()
        z = 1. - x - y
        values.append([x, y, z])
    data = pd.DataFrame(values, columns=["ポリマー", "良溶媒", "貧溶媒"])
    data.to_excel(r"tests\random_fraction.xlsx", index=False)

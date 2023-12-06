import re
import numpy as np
import pandas as pd
from ternary_data import TernaryData
from VIPS import VIPS
from ternary_diagram import Ternary
from typing import Union

def splitStrHierKeyString(comp_key: str) -> list:
    """ひとつづきの文字列を受け取りデリミタ":"で分解
       階層化されたJSONやYAMLデータにアクセスるための文字列を用意する

    Args:
        comp_key (str): 

    Returns:
        list: リスト形式のキー文字列
    """
    return re.sub(": *", ":", comp_key).split(":")

class EvalVIPS:
    def __init__(self):
        self.vips = VIPS()
        self.ternary_data = TernaryData()
        self.fraction = None
        self.deviation = None
        self.fraction_list = None
        self.deviation_list = None
        self.count = 0

    def askVIPSData(self) -> list:
        """VIPSクラスに問い合わせを行い、
           凝固浴突入直前の糸表面の組成を返してもらう

        Returns:
            list(float, float, float): 糸表面の組成
        """
        fraction = self.vips.surfaceFraction()
        return fraction

    def askPhaseSeparation(self, fraction: list) -> bool:
        # 現在保持している組成をTernaryDataクラスに問い合わせを行い、相分離が起きるかどうかを判定してもらう
        # TernaryDataクラスのisSeparateメソッドのラッパーファンクション
        return self.ternary_data.isSeparate(fraction[2], fraction[1], fraction[0])

    def askDeviation(self, fraction_init: list, fraction_after_absorption: list) -> float:
        # TernaryDataクラスにバイノーダル曲線からの乖離度を問い合わせ, 距離関数で返してもらう
        return self.ternary_data.deviationDistance(
            fraction_init[2], fraction_init[1], fraction_init[0],
            fraction_after_absorption[2], fraction_after_absorption[1], fraction_after_absorption[0]
        )

    def communicate(self) -> float:
        """設定紡糸条件でのVIPS判定を行う

        Returns:
            float: 初期原液組成, エアギャップ通過後の原液組成, エアギャップ通過後の原液組成とバイノーダル線の距離(バイノーダル線を跨いでいないときは負の値)
        """
        # 現在のパラメータで吸湿量計算実施を依頼、
        # さらに、吸湿後の組成を相図データと照らし合わせてVIPS発生の有無を問い合わせ
        # VIPSが起きる場合はバイノーダル線からの乖離具合を問い合わせる
        self.fraction_init = [ # 紡口吐出直後の原液の組成
                self.vips.current_param["Fiber"]["Init Non-Solvent Fraction"],
                self.vips.current_param["Fiber"]["Init Solvent Fraction"],
                self.vips.current_param["Fiber"]["Init Polymer Fraction"]
        ]
        self.fraction = self.askVIPSData() # 凝固浴突入前の原液組成
        # 20230419変更
        # if self.askPhaseSeparation(self.fraction):
        #    # VIPSが起きるときさらに乖離量を問い合わせする
        #     self.deviation = self.askDeviation(self.fraction_init, self.fraction)
        #     return self.fraction_init, self.fraction, self.deviation
        # else:
        #     return self.fraction_init, self.fraction, None
        self.deviation = self.askDeviation(self.fraction_init, self.fraction)
        if abs(self.deviation) > 10 : 
            print(f"deviation = {self.deviation} in count {self.count}")
            self.vips.exportAllVariables(f"./変数確認{self.count}.txt")
            self.count += 1
        return self.fraction_init, self.fraction, self.deviation
        

    def communicateLoop(self) -> list[float]:
        # 複数のパラメータでVIPS判定を行う場合
        self.fraction_init_list = []
        self.fraction_list  = []
        self.deviation_list = []
        for id, row in self.param_table.iterrows():
            self.updateParams(row)
            fraction_init, fraction, deviation = self.communicate()
            self.fraction_init_list.append(fraction_init)
            self.fraction_list.append(fraction)
            self.deviation_list.append(deviation)
        return self.fraction_init_list, self.fraction_list, self.deviation_list

    def setBinodalCurve(self, file_path: str):
        self.ternary_data.loadFitFunc(file_path)

    def setDefaultParam(self, file_path: str):
        # 吸湿量計算の基準となるパラメータを設定する
        self.default_param = self.vips.readParamFile(file_path)
        self.vips.current_param = self.default_param.copy()

    def setParamTable(self, file_path: str):
        # エクセルファイルを読み込む
        # self.param_table = pd.read_excel(file_path,skiprows=2,header=None) # usecolsは0スタート
        self.param_table = pd.read_excel(file_path,skiprows=1,header=None) # usecolsは0スタート

    def updateParams(self, row: pd.Series):
        # パラメータテーブルの書式が変わるたびに変更しなければならない
        # 単位の違いはここで吸収する
        # TODO: 書式入力ファイルを作成する
        # self.vips.current_param["Fiber"]["Init Polymer Fraction"]     = (row[1] + row[3]) * 0.01
        # self.vips.current_param["Fiber"]["Init Solvent Fraction"]     = row[2] * 0.01
        # self.vips.current_param["Fiber"]["Init Non-Solvent Fraction"] = (100. - row[1] - row[2] - row[3]) * 0.01
        # # self.vips.current_param["Fiber"]["Init Non-Solvent Fraction"] = row[3] * 0.01
        # # self.vips.current_param["Fiber"]["Inner Diameter"]            = row[4] 
        # # self.vips.current_param["Fiber"]["Outer Diameter"]            = row[5] 
        # self.vips.current_param["Air Gap"]["Temperature"]             = row[7] 
        # self.vips.current_param["Air Gap"]["Length"]                  = row[8] * 0.001
        # self.vips.current_param["Coagulation Bath"]["Temperature"]    = row[9] 


        self.vips.current_param["Fiber"]["Init Polymer Fraction"]     = (row[3] + row[4]) * 0.01
        self.vips.current_param["Fiber"]["Init Solvent Fraction"]     = \
             1.0 - self.vips.current_param["Fiber"]["Init Polymer Fraction"]
        self.vips.current_param["Fiber"]["Init Non-Solvent Fraction"] = 0.0
        self.vips.current_param["Air Gap"]["Temperature"]             = row[7] 
        self.vips.current_param["Air Gap"]["Length"]                  = row[8] * 0.001
        self.vips.current_param["Coagulation Bath"]["Temperature"]    = row[9] 

        self.vips.readParam(self.vips.current_param)

    def showResult(self, 
        polymer_name: str = "Polymer",
        solvent_name: str = "Solvent",
        non_solvent_name: str = "Non-Solvent",
        save_file_path: str = None
        ):
        """

        Args:
            polymer_name (str, optional): _description_. Defaults to "Polymer".
            solvent_name (str, optional): _description_. Defaults to "Solvent".
            non_solvent_name (str, optional): _description_. Defaults to "Non-Solvent".
            save_file_path (str, optional): _description_. Defaults to None.
        """
        tr = Ternary(polymer_name, solvent_name, non_solvent_name)
        # バイノーダル線プロット用の組成データを用意
        polymer = np.linspace(0, 1., 10)
        
        solvent = self.ternary_data.PSFitFunc(polymer)
        non_solvent = 1. - polymer - solvent
        tr.lines(polymer, solvent, non_solvent, "バイノーダル", "red", opacity=0.5)

        if self.deviation > 0: # 二相領域にある場合
            tr.scatter([self.fraction[2]], [self.fraction[1]], [self.fraction[0]], "", "red")
        else: # 一相領域にある場合
            tr.scatter([self.fraction[2]], [self.fraction[1]], [self.fraction[0]], "", "blue")
        if save_file_path != None:
            tr.saveHTML(save_file_path)
        tr.fig.show()

    def exportFractionLoop(self, 
        save_file_path: str = None,
        polymer_name: str = "Polymer",
        solvent_name: str = "Solvent",
        non_solvent_name: str = "Non-Solvent",
        ids: list = None,
        plot_fraction_init: bool = True,
        show: bool = True
        ):
        """communicateLoopを行った後にしか実行できない

        Args:
            polymer_name (str, optional): ポリマーの名前. Defaults to "Polymer".
            solvent_name (str, optional): 溶媒の名前. Defaults to "Solvent".
            non_solvent_name (str, optional): 貧溶媒の名前. Defaults to "Non-Solvent".
            ids (list, optional): レコードインデックス(グラフに表示する凡例ラベル). Defaults to None.
            save_file_path (str, optional): 保存先ファイルパス. Defaults to None.
            show (bool, optional): 画面上に表示するかどうか. Defaults to True.
        """
        tr = Ternary(polymer_name, solvent_name, non_solvent_name)
        polymer = np.linspace(0, 1., 10)
        solvent = self.ternary_data.PSFitFunc(polymer)
        non_solvent = 1. - polymer - solvent
        tr.lines(polymer, solvent, non_solvent, "バイノーダル", "red", opacity=0.5)
        if isinstance(ids, type(None)):
            for i, val in enumerate(zip(self.fraction_init_list, self.fraction_list, self.deviation_list)):
                fraction_init, fraction, deviation = val
                if deviation > 0:
                    tr.scatter([fraction[2]], [fraction[1]], [fraction[0]], i+1, "red")
                else:
                    tr.scatter([fraction[2]], [fraction[1]], [fraction[0]], i+1, "blue")
                if plot_fraction_init: # 紡口吐出直後の原液組成もプロットする場合
                    tr.scatter([fraction_init[2]], [fraction_init[1]], [fraction_init[0]], i+1, "green")
        else:
            for i, val in enumerate(zip(self.fraction_init_list, self.fraction_list, self.deviation_list, ids)):
                fraction_init, fraction, deviation, id = val
                # if deviation != None:
                if deviation > 0:
                    tr.scatter([fraction[2]], [fraction[1]], [fraction[0]], id, "red")
                else:
                    tr.scatter([fraction[2]], [fraction[1]], [fraction[0]], id, "blue")
                if plot_fraction_init: # 紡口吐出直後の原液組成もプロットする場合
                    tr.scatter([fraction_init[2]], [fraction_init[1]], [fraction_init[0]], id, "green")

        if save_file_path != None:
            tr.saveHTML(save_file_path)
        if show:
            tr.fig.show()

    def searchTc(self, Tmin: float = 15, Tmax: float = 70) -> float:
        """VIPSを起こすギリギリのチムニー温度を返す

        Args:
            Tmin (float): 探索を行う最小温度
            Tmax (float): 探索を行う最大温度

        Returns:
            float: チムニー温度 [℃]
        """
        T_tmp = self.vips.T_AG
        T_lim = [Tmin, Tmax]
        deviation = 1
        i = 1
        while abs(deviation) > 1e-09: # 二分探索によりVIPSを起こすギリギリのAG温度を探索
            T = (T_lim[0] + T_lim[1])/2
            self.vips.T_AG = T
            _, _, deviation = self.communicate()
            if deviation < 0:
                T_lim = [T, T_lim[1]]
            else:
                T_lim = [T_lim[0], T]
            i += 1
            if i == 1000:
                print("Tcを探索できませんでした")
                raise OverflowError
        self.vips.T_AG = T_tmp
        return T
        
if __name__ == "__main__":
    pass
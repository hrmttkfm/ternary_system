import sys
import pickle
from typing import Union
# import pandas as pd
import numpy as np
import pandas as pd
# from scipy.optimize import minimize
# from ternary_diagram import Ternary, default_colors, default_markers

def slope(x1: float, y1: float, x2: float, y2: float) -> float:
    """2次元カルテシアン座標系において
       (x1, y1), (x2, y2)の2点を通る線分の傾きを返す

    Args:
        x1 (float): 1点目のx座標
        y1 (float): 1点目のy座標
        x2 (float): 2点目のx座標
        y2 (float): 2点目のy座標

    Returns:
        float: 傾きの値
    """
    return (y2 - y1) / (x2 - x1)

def interception(x1: float, y1: float, x2: float, y2: float) -> float:
    """2次元カルテシアン座標系において
       (x1, y1), (x2, y2)の2点を通る線分の切片を返す

    Args:
        x1 (float): 1点目のx座標
        y1 (float): 1点目のy座標
        x2 (float): 2点目のx座標
        y2 (float): 2点目のy座標

    Returns:
        float: 切片の
    """
    return y1 - slope(x1, y1, x2, y2) * x1

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """2次元カルテシアン座標系において
       (x1, y1), (x2, y2)の2点を通る線分の長さを返す

    Args:
        x1 (float): 1点目のx座標
        y1 (float): 1点目のy座標
        x2 (float): 2点目のx座標
        y2 (float): 2点目のy座標

    Returns:
        float: 距離 (>=0.)
    """
    return np.sqrt( (y2 - y1)**2 + (x2 - x1)**2 )

def crossPoint(a1: float, b1: float, a2: float, b2: float) -> Union[float, float]:
    """2次元カルテシアン座標系において
       2本の直線の交点を返す

    Args:
        a1 (float): 1本目の直線の傾き
        b1 (float): 1本目の直線の切片
        a2 (float): 2本目の直線の傾き
        b2 (float): 2本目の直線の切片

    Returns:
        Union[float, float]: 交点のx座標とy座標
    """
    if abs(a1 - a2) < 1e-09:
        print("2本の直線は交点を持ちません.")
        print(f"a1 = {a1}, b1 = {b1}")
        print(f"a2 = {a2}, b2 = {b2}")
        raise ValueError
    return - (b1-b2)/(a1-a2), (a1*b2-a2*b1)/(a1-a2)


# 良溶媒頂点からポリマー頂点へ向かうベクトル(規格化済み)
vSP = np.array([0.5, 0.5*np.sqrt(3.)])
# ポリマー頂点から貧溶媒頂点へ向かうベクトル(規格化済み)
vPN = np.array([0.5, -0.5*np.sqrt(3.)])
# 貧溶媒頂点から良溶媒頂点へ向かうベクトル(規格化済み)
vNS = np.array([-1., 0.])

vSPinv = np.array([1.,1.])
vPNinv = np.array([1./np.sqrt(3.), -1./np.sqrt(3.)])

def PStoUV(polymer: float | np.ndarray | pd.Series, 
           solvent: float | np.ndarray | pd.Series) \
        -> Union[float, float] | Union[np.ndarray, np.ndarray] | Union[pd.Series, pd.Series]:
    """ポリマー分率と良溶媒分率を3角線図の2Dカルテシアン座標系
       (座標軸はUとV)に変換する

    Args:
        polymer (float | np.ndarray | pd.Series): ポリマーの重量分率
        solvent (float | np.ndarray | pd.Series): 良溶媒分率

    Returns:
        Union[float, float] | Union[np.ndarray, np.ndarray] | Union[pd.Series, pd.Series]: U座標とV座標
    """
    non_solvent = 1. - polymer - solvent # 貧溶媒の分率を計算
    if type(polymer) == np.ndarray: # 配列形式で分率を渡されたとき
        assert(len(polymer) == len(solvent))
        assert(np.all(non_solvent >= 0.))

        # UV座標系での座標値を配列に格納
        points = np.tile(polymer    [:,None],(1,2)) * np.tile(vSP, (len(polymer),1)) \
               + np.tile(non_solvent[:,None],(1,2)) * np.tile(vPN, (len(polymer),1))
        return points[:, 0], points[:, 1]
    elif type(polymer) == pd.Series:
        Us, Vs = PStoUV(polymer.values, solvent.values)
        return pd.Series(Us), pd.Series(Vs)
    else: # スカラー形式で分率を渡されたとき
        assert(non_solvent >= 0.)
        point = polymer * vSP + non_solvent * vPN
        return point[0], point[1]

def UVtoPS(U: float | np.ndarray | pd.Series, 
           V: float | np.ndarray | pd.Series) \
        -> Union[float, float] | Union[np.ndarray, np.ndarray] | Union[pd.Series, pd.Series]:
    """角線図の2Dカルテシアン座標系(座標軸はUとV)
       をポリマー分率と良溶媒分率に変換する

    Args:
        U (float | np.ndarray | pd.Series): U座標値
        V (float | np.ndarray | pd.Series): V座標値

    Returns:
        Union[float, float] | Union[np.ndarray, np.ndarray] | Union[pd.Series, pd.Series]: ポリマー分率と良溶媒分率
    """
    if type(U) == np.ndarray: # 配列形式でU, V座標値を渡されたとき
        assert(len(U) == len(V))
        # UV座標系での座標値を配列に格納
        points = np.tile(U[:,None],(1,2)) * np.tile(vSPinv, (len(U),1)) \
               + np.tile(V[:,None],(1,2)) * np.tile(vPNinv, (len(U),1))
        solvents = 1. - points[:,0] - points[:,1]
        return points[:, 0], solvents
    elif type(U) == pd.Series:
        Ps, Ss = UVtoPS(U.values, V.values)
        return pd.Series(Ps), pd.Series(Ss)
    else: # スカラー形式で分率を渡されたとき
        point = U * vSPinv + V * vPNinv
        solvent = 1. - point[0] - point[1]
        return point[0], solvent

def UVlineToPSLine(slope: float, interception: float) -> Union[float, float]:
    """UV座標系における直線をポリマー分率 v.s. 良溶媒分率における直線に変換

    Args:
        slope (float): UV座標系に於ける直線の傾き
        interception (float): UV座標系における直線の切片

    Returns:
        Union[float, float]: ポリマー分率・良溶媒分率座標系に於ける直線の傾きと切片
    """
    return -(1+(np.sqrt(3.)-slope)/(np.sqrt(3.)+slope)), (1+2./(np.sqrt(3)+slope)*interception)

class TernaryData:
    """ポリマー・良溶媒・貧溶媒、3成分系のデータを取り扱う
    """
    def __init__(self, polymer: float | np.ndarray = None, 
                       solvent: float | np.ndarray = None, 
                       non_solvent : float | np.ndarray= None, 
                       temperature: str = None):
        """コンストラクタ

        Args:
            polymer (float | np.ndarray, optional): ポリマーの体積分率. Defaults to None.
            solvent (float | np.ndarray, optional): 溶媒の体積分率. Defaults to None.
            non_solvent (float | np.ndarray, optional): 貧溶媒の体積分率. Defaults to None.
            temperature (str, optional): 温度. Defaults to None.
        """
        self.readData(polymer, solvent, non_solvent, temperature)
        self.fitFunc = None

    def readData(self, polymer: float | np.ndarray = None, 
                       solvent: float | np.ndarray = None, 
                       non_solvent : float | np.ndarray= None, 
                       temperature: str = None):
        """実験により得られたデータを読み込む

        Args:
            polymer (float | np.ndarray, optional): ポリマーの体積分率. Defaults to None.
            solvent (float | np.ndarray, optional): 溶媒の体積分率. Defaults to None.
            non_solvent (float | np.ndarray, optional): 貧溶媒の体積分率. Defaults to None.
            temperature (str, optional): 温度. Defaults to None.
        """
        self.polymer = polymer
        self.solvent = solvent
        self.non_solvent = non_solvent
        self.temperature = temperature

    # def fitData(self, deg: int = 1):
    #     """バイノーダル線を多項式関数でフィッティングする

    #     Args:
    #         deg (int, optional): 多項式次元. Defaults to 1.

    #     Note: 
    #         現状では1次でしかうまくフィッティングできない
    #     """
    #     self.fitFunc = np.poly1d(np.polyfit(x=self.polymer, y=self.solvent, deg=deg))

    def fitData(self, deg: int = 1):
        """バイノーダル線をUV線図上で多項式関数によりフィッティングする

        Args:
            deg (int, optional): 多項式次元. Defaults to 1.

        Note: 
            現状では1次でしかうまくフィッティングできない
        """
        # ポリマー・溶媒の体積分率をUV座標系に変換
        Us, Vs = PStoUV(self.polymer, self.solvent)
        self.fitFunc = np.poly1d(np.polyfit(x=Us, y=Vs, deg=deg))
        self.__calcFitFuncSlopeAndInc()

    def exportFitFunc(self, file_path: str = "./binodalFitFunc.pkl"):
        """バイノーダル線をフィッティングした関数をpklファイルに出力する

        Args:
            file_path (str, optional): 出力するファイルパス Defaults to "./binodalFitFunc.pkl".
        """
        if not file_path.split(".")[-1] in ["pkl", "pickle"]:
            print("対応しないファイルです. ", file = sys.err)
            raise ValueError
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(self.fitFunc, f)
        except Exception as e:
            print("ファイル出力に失敗しました. ", file=sys.stderr)
            print(e, file=sys.stderr)
            exit(1)

    def loadFitFunc(self, file_path: str = "./binodalFitFunc.pkl"):
        """エクスポートしたバイノーダル線のフィッティング関数を読み込む

        Args:
            file_path (str, optional): エクスポートしたバイノーダル線のファイルパス. Defaults to "./binodalFitFunc.pkl".
        """
        if not file_path.split(".")[-1] in ["pkl", "pickle"]:
            print("対応しないファイルです. ", file = sys.err)
            raise ValueError
        try:
            with open(file_path, 'rb') as f:
                self.fitFunc = pickle.load(f)
        except Exception as e:
            print('ファイルパスを確認してください. ', file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(1)
        self.__calcFitFuncSlopeAndInc()

    def __calcFitFuncSlopeAndInc(self):
        """バイノーダル曲線をフィッティングした直線の傾きと切片を格納する
        """
        # 傾き・切片を計算するためのとりあえずの2点を計算
        U1 = 0; U2 = 1 
        V1 = self.fitFunc(U1)
        V2 = self.fitFunc(U2)
        self.fit_slope = slope(U1, V1, U2, V2)
        self.fit_inc   = interception(U1, V1, U2, V2)

    def PSFitFunc(self, polymer):
        """ポリマー分率・溶媒分率座標空間におけるバイノーダル線を返す

        Returns:
        """
        slope_ps, inc_ps = UVlineToPSLine(self.fit_slope, self.fit_inc)
        return slope_ps * polymer + inc_ps

    # def isSeparate(self, p: float, s: float, n_s: float) -> bool:
    #     """ある組成の液が相分離するかどうかを判定する

    #     Args:
    #         p (float): ポリマー体積分率
    #         s (float): 溶媒体積分率
    #         n_s (float): 貧溶媒体積分率

    #     Returns:
    #         bool: バイノーダル線の内側であればTrue
    #               外側であればFalseを返す
    #     """
    #     if not isinstance(self.fitFunc, type(None)): 
    #         return s < self.fitFunc(p)
    #     else:
    #         print("フィッティング関数が設定されていません.")
    #         raise ValueError

    def isSeparate(self, p: float, s: float, n_s: float) -> bool:
        """ある組成の液が相分離するかどうかを判定する

        Args:
            p (float): ポリマー体積分率
            s (float): 溶媒体積分率
            n_s (float): 貧溶媒体積分率

        Returns:
            bool: バイノーダル線の内側であればTrue
                  外側であればFalseを返す
        """
        # 座標変換
        U, V = PStoUV(p, s)
        if not isinstance(self.fitFunc, type(None)): 
            return V < self.fitFunc(U)
        else:
            print("フィッティング関数が設定されていません.")
            raise ValueError

    # def deviationDistance(self, 
    #        p1: float, s1: float, n_s1: float, 
    #        p2: float, s2: float, n_s2: float, 
    # ) -> float:
    #     """吸湿前原液組成と吸湿後原液組成を結ぶ線分と
    #        バイノーダル線の交点から、吸湿後組成までの距離を返す

    #     Args:
    #         p1 (float): 初期ポリマー重量分率
    #         s1 (float): 初期溶媒重量分率
    #         n_s1 (float): 初期貧溶媒重量分率
    #         p2 (float): 吸湿後ポリマー重量分率
    #         s2 (float): 吸湿後溶媒重量分率
    #         n_s2 (float): 吸湿後貧溶媒重量分率

    #     Returns:
    #         float: 吸湿前原液組成と吸湿後原液組成を結ぶ線分と
    #                バイノーダル線の交点から、吸湿後組成までの距離
    #                線分と直線が交点を持たない場合は負の値を返す
    #     """
    #     if p1 < 0. or 1. < p1:
    #         print("不正な初期ポリマー分率です. ")
    #         print(f"p1 = {p1}")
    #     if s1 < 0. or 1. < s1:
    #         print("不正な初期溶媒分率です. ")
    #         print(f"s1 = {s1}")
    #     if n_s1 < 0. or 1. < n_s1:
    #         print("不正な初期貧溶媒分率です. ")
    #         print(f"n_s1 = {n_s1}")
    #     if p2 < 0. or 1. < p2:
    #         print("不正な初期ポリマー分率です. ")
    #         print(f"p2 = {p2}")
    #     if s2 < 0. or 1. < s2:
    #         print("不正な初期溶媒分率です. ")
    #         print(f"s2 = {s2}")
    #     if n_s2 < 0. or 1. < n_s2:
    #         print("不正な初期貧溶媒分率です. ")
    #         print(f"n_s2 = {n_s2}")
    #     # 吸湿前原液組成と吸湿後原液組成を結ぶ直線の傾き
    #     dope_slope = slope(p1, s1, p2, s2)
    #     # 吸湿前原液組成と吸湿後原液組成を結ぶ直線の切片
    #     dope_inc   = interception(p1, s1, p2, s2)
    #     # 交点の組成、ポリマーと溶媒の重量分率
    #     pc, sc     = crossPoint(self.fit_slope, self.fit_inc, dope_slope, dope_inc)
    #     d = distance(p2, s2, pc, sc)
    #     if d > 1.:
    #         print("乖離度が1を超えました.")
    #         print(f"p1 = {p1}, s1 = {s1}")
    #         print(f"pc = {pc}, sc = {sc}")
    #         print(f"p2 = {p2}, s2 = {s2}")
    #         print(f"distance = {d}")
    #         print(f"fit_slope  = {self.fit_slope}, fit_inc = {self.fit_inc}")
    #         print(f"dope_slope = {dope_slope}, dope_inc = {dope_inc}")
    #     if self.isSeparate(p2, s2, n_s2):
    #         return d
    #     else:
    #         return - d

    def deviationDistance(self, 
           p1: float, s1: float, n_s1: float, 
           p2: float, s2: float, n_s2: float, 
    ) -> float:
        """UV平面上で
           吸湿前原液組成と吸湿後原液組成を結ぶ線分と
           バイノーダル線の交点から、吸湿後組成までの距離を返す

        Args:
            p1 (float): 初期ポリマー重量分率
            s1 (float): 初期溶媒重量分率
            n_s1 (float): 初期貧溶媒重量分率
            p2 (float): 吸湿後ポリマー重量分率
            s2 (float): 吸湿後溶媒重量分率
            n_s2 (float): 吸湿後貧溶媒重量分率

        Returns:
            float: 吸湿前原液組成と吸湿後原液組成を結ぶ線分と
                   バイノーダル線の交点から、吸湿後組成までの距離
                   線分と直線が交点を持たない場合は負の値を返す
        """
        # 吸湿前後の原液組成をUV座標系に変換
        U1, V1 = PStoUV(p1, s1) # 吸湿前組成
        U2, V2 = PStoUV(p2, s2) # 吸湿後組成
        # 吸湿前原液組成と吸湿後原液組成を結ぶ直線の傾き
        dope_slope = slope(U1, V1, U2, V2)
        # 吸湿前原液組成と吸湿後原液組成を結ぶ直線の切片
        dope_inc   = interception(U1, V1, U2, V2)
        # 交点の組成、ポリマーと溶媒の重量分率
        Uc, Vc     = crossPoint(self.fit_slope, self.fit_inc, dope_slope, dope_inc)
        d = distance(U2, V2, Uc, Vc)
        if d > 1.:
            print("乖離度が1を超えました.")
            print(f"U1 = {U1}, V1 = {V1}")
            print(f"Uc = {Uc}, Vc = {Vc}")
            print(f"U2 = {U2}, V2 = {V2}")
            print(f"distance = {d}")
            print(f"fit_slope  = {self.fit_slope}, fit_inc = {self.fit_inc}")
            print(f"dope_slope = {dope_slope}, dope_inc = {dope_inc}")
        if self.isSeparate(p2, s2, n_s2):
            return d
        else:
            return - d
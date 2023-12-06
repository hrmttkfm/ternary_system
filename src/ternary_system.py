import sys
import pickle
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from ternary_diagram import Ternary, default_colors, default_markers
from component import Component
from phase import Phase

class TernarySpinodal:
    """1. 貧溶媒, 2. 良溶媒, 3. ポリマーの3成分系
       をFlory-Hugginsモデルを用いて扱うクラス
    """
    def __init__(self, phase: Phase):
        self.phase = phase.copy() 
        self.bnds = ( # scipy.optimize.minimizeする際の探索範囲
        (0.00000000001, 0.9999999999), # 良溶媒体積分率
        )

    def costFunc(self):
        """コスト関数を計算する
        """
        return abs(self.phase.G22()*self.phase.G33() - np.power(self.phase.G23(),2))

    def __costFuncWrapper(self,
            phi: np.ndarray):
        """costFuncのラッパーファンクション
           scipy.optimize.minimizeを使うため

        Args:
            phi (np.ndarray): 良溶媒の体積分率

        Returns:
            float: costFunc
        """

        self.phase.comp2.phi = phi[0]
        return self.costFunc()

    def spinodal(self, phase_phi3):
        # 最適化計算
        res_all = []
        for i in range(len(phase_phi3)):
            print(i)
            self.phase.comp3.phi = phase_phi3[i]

            res = minimize(fun=self.__costFuncWrapper, 
                # method='Nelder-Mead', # o
                method='Powell', # x
                # method='CG', # ×
                # method='BFGS', # ×
                # method='Newton-CG', # ×
                # method='L-BFGS-B', # ×
                # method='TNC', # ×
                # method='COBYLA', # ×
                # method='SLSQP', # o
                # method='trust-constr' # x
                # method='dogleg', # x
                # method='trust-ncg', # x
                # method='trust-exact', # ×
                # method='trust-krylov', # ×
                x0=[(1. - self.phase.comp3.phi)*0.5],
                bounds=self.bnds,
                tol=1e-20)#, options={"disp": True})
            self.phase.comp2.phi = res.x[0]
            self.phase.comp1.phi = 1. - (self.phase.comp2.phi + self.phase.comp3.phi)
            res_all.append([
                self.phase.comp1.phi,
                self.phase.comp2.phi,
                self.phase.comp3.phi,
            ])
        phis_arr = np.array(res_all, dtype=float) # 全ての点のデータをnumpy配列に変換

        # 各成分の密度を縦ベクトル化
        rho_arr = np.array([self.phase.comp1.rho,
                            self.phase.comp2.rho,
                            self.phase.comp3.rho], dtype=float)
        rho_arr_tile = np.tile(rho_arr, reps=(len(phis_arr),1))

        # 各点における単位体積当たりの総質量ベクトルを作成し3列に拡張(複製)
        mass_arr_tile = np.tile(np.dot(phis_arr, rho_arr[:,None]), 3)
        # 質量分率で表した配列
        ws_arr = phis_arr * rho_arr_tile / mass_arr_tile
        return ws_arr

class TernaryBinodal:
    """1. 貧溶媒, 2. 良溶媒, 3. ポリマーの3成分系
       をFlory-Hugginsモデルを用いて扱うクラス
    """
    def __init__(self, phase: Phase):
        self.phaseR = phase.copy() # ポリマーリッチ相
        self.phaseL = phase.copy() # ポリマーリーン相
        self.bnds = ( # scipy.optimize.minimizeする際の探索範囲
        (0.00000000001, 0.9999999999), # ポリマーリッチ相の良溶媒体積分率探索範囲
        (0.00000000001, 0.9999999999), # ポリマーリッチ相のポリマー体積分率探索範囲
        (0.00000000001, 0.9999999999)  # ポリマーリーン相の良溶媒体積分率探索範囲
        )

    def costFunc(self):
        """コスト関数を計算する
        """
        # 貧溶媒極値付近ではこちらの方が良い
        # return np.power(         self.f1(),2) / np.power((self.phaseR.comp1.phi - self.phaseL.comp1.phi),4) \
        #      + np.power(self.phaseL.s * self.f2(),2) / np.power((self.phaseR.comp2.phi - self.phaseL.comp2.phi),4) \
        #      + np.power(self.phaseL.r * self.f3(),2) / np.power((self.phaseR.comp3.phi - self.phaseL.comp3.phi),4) 
        # 頂点付近ではこちらの方が良い
        return (np.power(                self.f1(),2) \
              + np.power(self.phaseL.s * self.f2(),2) \
              + np.power(self.phaseL.r * self.f3(),2) )

    def __costFuncWrapper(self,
            phis: np.ndarray):
        """costFuncのラッパーファンクション
           scipy.optimize.minimizeを使うため

        Args:
            phis (np.ndarray): ポリマーリッチ相の良溶媒、ポリマーの体積分率
                               ポリマーリーン相の良溶媒体積分率

        Returns:
            float: costFunc
        """

        self.phaseR.comp2.phi = phis[0] 
        self.phaseR.comp3.phi = phis[1] 
        self.phaseL.comp2.phi = phis[2] 
        return self.costFunc()

    def f1(self):
        """ポリマーリッチ相とポリマーリーン相間での
           貧溶媒ケミカルポテンシャルの差を計算する

        Returns:
            float: Δμ1^R/RT - Δμ1^L/RT
        """
        return self.phaseR.mu1RT() - self.phaseL.mu1RT()

    def f2(self):
        """ポリマーリッチ相とポリマーリーン相間での
           良溶媒ケミカルポテンシャルの差を計算する

        Returns:
            float: Δμ2^R/RT - Δμ2^L/RT
        """
        return self.phaseR.mu2RT() - self.phaseL.mu2RT()

    def f3(self):
        """ポリマーリッチ相とポリマーリーン相間での
           ポリマーケミカルポテンシャルの差を計算する

        Returns:
            float: Δμ3^R/RT - Δμ3^L/RT
        """
        return self.phaseR.mu3RT() - self.phaseL.mu3RT()

    def binodal(self, phaseL_phi3):
        # 最適化計算
        res_all = []
        for i in range(len(phaseL_phi3)):
            print(i)
            self.phaseL.comp3.phi = phaseL_phi3[i]

            res = minimize(fun=self.__costFuncWrapper, 
                # 最小二乗法メソッド
                # method='Nelder-Mead', # o
                # method='Powell', # x
                # method='CG', # ×
                # method='BFGS', # ×
                # method='Newton-CG', # ×
                # method='L-BFGS-B', # ×
                # method='TNC', # ×
                # method='COBYLA', # ×
                method='SLSQP', # o
                # method='trust-constr' # x
                # method='dogleg', # x
                # method='trust-ncg', # x
                # method='trust-exact', # ×
                # method='trust-krylov', # ×
                x0=[0.2, 0.5, (1. - self.phaseL.comp3.phi)*0.5], # 
                bounds=self.bnds, # 変数の探索範囲
                tol=1e-20)#, options={"disp": True})
            self.phaseR.comp2.phi, self.phaseR.comp3.phi, self.phaseL.comp2.phi = res.x
            self.phaseR.comp1.phi = 1. - (self.phaseR.comp2.phi + self.phaseR.comp3.phi)
            self.phaseL.comp1.phi = 1. - (self.phaseL.comp2.phi + self.phaseL.comp3.phi)
            res_all.append([
                self.phaseR.comp1.phi,
                self.phaseR.comp2.phi,
                self.phaseR.comp3.phi,
                self.phaseL.comp1.phi,
                self.phaseL.comp2.phi,
                self.phaseL.comp3.phi
            ])
        arr = np.array(res_all, dtype=float) # 全ての点のデータをnumpy配列に変換
        rich = arr[:, 0:3] # 0~1列目を抽出 -> ポリマーリッチ相の良溶媒とポリマー
        lean = arr[:, 3:] # 2列目を抽出 -> ポリマーリーン相の良溶媒
        # リッチ相とリーン相のデータを縦に結合
        phis_arr = np.vstack((rich,lean))

        # 各成分の密度を縦ベクトル化
        rho_arr = np.array([self.phaseR.comp1.rho,
                            self.phaseR.comp2.rho,
                            self.phaseR.comp3.rho], dtype=float)
        rho_arr_tile = np.tile(rho_arr, reps=(len(phis_arr),1))

        # 各点における単位体積当たりの総質量ベクトルを作成し3列に拡張(複製)
        mass_arr_tile = np.tile(np.dot(phis_arr, rho_arr[:,None]), 3)
        # 質量分率で表した配列
        ws_arr = phis_arr * rho_arr_tile / mass_arr_tile
        return ws_arr

    def tieLineFromBinodal(self, binodal_arr):
        """

        Args:
            binodal_arr (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        if len(binodal_arr) % 2 != 0:
            # 偶数行でないとエラー
            print("Binodal Data must have even length")
            raise ValueError
        else:
            rich, lean = np.split(binodal_arr,2)
            tie_arr = np.hstack((rich, lean))
            return tie_arr


if __name__ == "__main__":
    # n_solvent = Component(18, 1., "Water")
    # solvent   = Component(96.6, 1.026, "NMP")
    # polymer   = Component(43795.6, 1.37, "PES")
    # phase_init = Phase(n_solvent, solvent, polymer, 0.5, 0.279, 1.7)

    # CA/Acetone/H2O系
    # n_solvent = Component(1, 1., "Water")
    # solvent   = Component(4, 0.784, "Acetone")
    # polymer   = Component(500, 1.3, "Acetylcellulose")
    # phase_init = Phase(n_solvent, solvent, polymer, -0.3, 0.2, 1.)

    # EVAL/DMSO/H2O系
    # n_solvent = Component(18, 1., "Water")
    # solvent   = Component(71.29, 1.096, "DMSO")
    # polymer   = Component(47863, 1.17, "EVOH")
    # phase_init = Phase(n_solvent, solvent, polymer, 0.5927, -1.2 + 0.02, 1.956)

    # PSF/NMP/H2O系
    # Y. Yip, A.J. McHug, Journal of Membrane Science, 271, p.163-176 (2006)
    n_solvent = Component(18, 1., "Water")
    solvent   = Component(71.29, 1.03, "NMP")
    polymer   = Component(20270, 1.24, "PSF")
    # phase_init = Phase(n_solvent, solvent, polymer, lambda x, y :  0.785 + y/(x+y) * 0.665, 0.24, 2.5)
    phase_init = Phase(n_solvent, solvent, polymer, 0.785 + 0.5 * 0.665, 0.24, 2.5)

    binodal_system    = TernaryBinodal(phase_init)
    spinodal_system    = TernarySpinodal(phase_init)

    # バイノーダル曲線の計算
    binodal = pd.DataFrame(
        binodal_system.binodal(
            # np.hstack((np.logspace(-38, -2.5, 60),np.logspace(-2.5, -1.2, 6)))) # CA/Acetone/H2O
            # np.hstack((np.logspace(-300, -2.5, 60),np.logspace(-2.3, -2.1, 3)))) # EVAL/DMSO/H2O
            np.hstack((np.logspace(-300, -2.5, 200),np.logspace(-2.4, -1.9, 4)))) # PSF/NMP/H2O
                        , columns = ['貧溶媒', '良溶媒', 'ポリマー'])
    binodal.to_excel("binodal.xlsx")
    tie = pd.DataFrame(binodal_system.tieLineFromBinodal(binodal.values), columns = ['R貧溶媒', 'R良溶媒', 'Rポリマー', 'L貧溶媒', 'L良溶媒', 'Lポリマー'])
    tie.to_excel("tie_line.xlsx")

    # スピノーダル曲線の計算
    # spinodal = pd.DataFrame(
    #     spinodal_system.spinodal(
    #         np.linspace(0.001, 0.6, 100))
    #                     , columns = ['貧溶媒', '良溶媒', 'ポリマー'])
    # spinodal.to_excel("spinodal.xlsx")

    tr = Ternary(polymer.name, solvent.name, n_solvent.name)
    # タイラインのプロット
    tie = pd.read_excel("tie_line.xlsx")
    tr.tieLine(tie["Rポリマー"], tie["R良溶媒"], tie["R貧溶媒"],
               tie["Lポリマー"], tie["L良溶媒"], tie["L貧溶媒"])
    # スピノーダルラインのプロット
    # spinodal = pd.read_excel("spinodal.xlsx")
    # tr.spinodalLine(spinodal["ポリマー"], spinodal["良溶媒"], spinodal["貧溶媒"], "スピノーダル")
    # バイノーダルラインのプロット
    binodal = pd.read_excel("binodal.xlsx")
    tr.binodalLine(binodal["ポリマー"], binodal["良溶媒"], binodal["貧溶媒"], "バイノーダル")

    prefix = "{}_{}_{}".format(polymer.name, solvent.name, n_solvent.name)
    tr.saveHTML("{}.html".format(prefix))
    tr.saveStaticImage("{}.svg".format(prefix))


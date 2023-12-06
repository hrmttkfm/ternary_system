import numpy as np
from component import Component

class Phase:
    """3成分からなるPhase(相)を表すクラス
    """
    def __init__(self, component1: Component, 
                       component2: Component, 
                       component3: Component,
                       chi12: any, 
                       chi23: any, 
                       chi13: any):
        """コンストラクタ

        Args:
            component1 (Component): 貧溶媒
            component2 (Component): 良溶媒
            component3 (Component): ポリマー
            chi12 (float): 貧溶媒・良溶媒間のχパラメータ
            chi23 (float): 良溶媒・ポリマー間のχパラメータ
            chi13 (float): 貧溶媒・ポリマー間のχパラメータ
        """
        self.comp1 = component1 # 貧溶媒
        self.comp2 = component2 # 良溶媒
        self.comp3 = component3 # ポリマー
        self.chi12 = chi12 # χ12
        self.chi23 = chi23 # χ23
        self.chi13 = chi13 # χ13
        self.s = self.comp1.nu / self.comp2.nu # 貧溶媒と良溶媒のモル体積比率
        self.r = self.comp1.nu / self.comp3.nu # 貧溶媒とポリマーモル体積比率
        print("s = ",self.s)
        print("r = ",self.r)

    def copy(self):
        """オブジェクトのコピー関数

        Returns:
            Phase: Phaseオブジェクト
        """
        obj_copy = Phase(self.comp1.copy(), self.comp2.copy(), self.comp3.copy(),
                        self.chi12, self.chi23, self.chi13)
        return obj_copy

    def getPhis(self) -> tuple[float, float, float]: 
        """現在の相内体積分率組成を返す

        Returns:
            tuple[float, float, float]: (貧溶媒体積分率, 良溶媒体積分率, ポリマー体積分率)
        """
        return self.comp1.phi, self.comp2.phi, self.comp3.phi

    def getXs(self) -> tuple[float, float, float]: 
        """現在の相内の体積分率からモル分率を計算して返す

        Returns:
            tuple[float, float, float]: (貧溶媒モル分率, 良溶媒モル分率, ポリマーモル分率)
        """
        
        phi1, phi2, phi3 = self.getPhis()
        denom = phi1 + self.s*phi2 + self.r*phi3
        return phi1/denom, self.s*phi2/denom, self.r*phi3/denom

    def setPhis(self, phi1: float, phi2: float, phi3: float):
        """体積分率組成を設定する

        Args:
            phi1 (float): 貧溶媒体積分率
            phi2 (float): 良溶媒体積分率
            phi3 (float): ポリマー体積分率
        """
        assert (phi1+phi2+phi3 - 1.) < 0.00001, "体積分率の合計値が1.ではありません"
        self.comp1.phi, self.comp2.phi, self.comp3.phi = [phi1, phi2, phi3]

    def mu1RT(self) -> float: 
        """貧溶媒について, Δμ1=(相中のケミカルポテンシャル)-(純粋なケミカルポテンシャル)
           を計算する

        Returns:
            float: Δμ1/RT
        """
        chi12, chi23, chi13 = self.calcChiAll()
        self.comp1.phi = 1. - self.comp2.phi - self.comp3.phi
        return np.log(self.comp1.phi) + 1 - self.comp1.phi - self.s*self.comp2.phi - self.r*self.comp3.phi \
            + (chi12*self.comp2.phi + chi13*self.comp3.phi) * (1 - self.comp1.phi) \
            - self.s*chi23*self.comp2.phi*self.comp3.phi

    def mu2RT(self) -> float: 
        """良溶媒について, Δμ2=(相中のケミカルポテンシャル)-(純粋なケミカルポテンシャル)
           を計算する

        Returns:
            float: Δμ2/RT
        """
        chi12, chi23, chi13 = self.calcChiAll()
        self.comp1.phi = 1. - self.comp2.phi - self.comp3.phi
        return 1/self.s * (self.s*np.log(self.comp2.phi) + self.s - self.comp1.phi - self.s*self.comp2.phi - self.r*self.comp3.phi \
            + (chi12*self.comp1.phi + self.s*chi23*self.comp3.phi) * (1 - self.comp2.phi) \
            - chi13*self.comp1.phi*self.comp3.phi)

    def mu3RT(self) -> float: 
        """ポリマーについて, Δμ3=(相中のケミカルポテンシャル)-(純粋なケミカルポテンシャル)
           を計算する

        Returns:
            float: Δμ3/RT
        """
        chi12, chi23, chi13 = self.calcChiAll()
        self.comp1.phi = 1. - self.comp2.phi - self.comp3.phi
        return 1/self.r * (self.r*np.log(self.comp3.phi) + self.r - self.comp1.phi - self.s*self.comp2.phi - self.r*self.comp3.phi \
            + (chi13*self.comp1.phi + self.s*chi23*self.comp2.phi) * (1 - self.comp3.phi) \
            - chi12*self.comp1.phi*self.comp2.phi)

    def G22(self):
        chi12 = self.calcChi12()
        self.comp1.phi = 1. - self.comp2.phi - self.comp3.phi
        return 1/self.comp1.phi + self.s/self.comp2.phi - 2*chi12

    def G23(self):
        chi12 = self.calcChi12()
        chi13 = self.calcChi13()
        chi23 = self.calcChi23()
        self.comp1.phi = 1. - self.comp2.phi - self.comp3.phi
        return 1/self.comp1.phi - (chi12+chi13) + self.s*chi23

    def G33(self):
        chi13 = self.calcChi13()
        self.comp1.phi = 1. - self.comp2.phi - self.comp3.phi
        return 1/self.comp1.phi + self.r/self.comp3.phi - 2*chi13

    def calcChi12(self):
        if type(self.chi12) == float:
            chi12 = self.chi12
        else:
            chi12 = self.chi12.val(self.comp1.phi, self.comp2.phi)
        return chi12

    def calcChi23(self):
        if type(self.chi23) == float:
            chi23 = self.chi23
        else:
            chi23 = self.chi23.val(self.comp1.phi, self.comp2.phi)
        return chi23

    def calcChi13(self):
        if type(self.chi13) == float:
            chi13 = self.chi13
        else:
            chi13 = self.chi13.val(self.comp1.phi, self.comp2.phi)
        return chi13

    def calcChiAll(self) -> tuple[float, float, float]:
        chi12 = self.calcChi12()
        chi23 = self.calcChi23()
        chi13 = self.calcChi13()
        return chi12, chi23, chi13
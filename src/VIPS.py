import json
import yaml
import numpy as np
import sys
import matplotlib.pyplot as plt
import japanize_matplotlib

# 気体定数
R = 8.31446 # [J/K/mol]
# 水の分子量
Mw = 18 # [g/mol]
# 空気の分子量
Mair = 28.966 # [g/mol]

class VIPS:
    def __init__(self):
        pass

    def __copy__(self):
        vips = VIPS()
        vips.readParam(self.current_param)
        return vips

    def readParam(self, param: dict) -> dict:
        """吸湿量計算に必要なパラメータを読み込み, 読み込んだパラメータを辞書で返す

        Args:
            param (dict): 読み込むパラメータ

        Returns:
            dict: 読み込んだパラメータ
        """
        self.current_param = param # 現在のパラメータを格納
        try:
            if "Air Gap" in param:
                param_AG = param['Air Gap']
                if "Length" in param_AG:
                    self.L_AG = param_AG['Length']
                if "Diameter" in param_AG:
                    self.d_AG = param_AG['Diameter']
                if "Temperature" in param_AG:
                    self.T_AG = param_AG['Temperature']
                if "Pressure" in param_AG:
                    self.P_AG = param_AG['Pressure']
            if "Fiber" in param:
                param_Fiber = param['Fiber']
                if "Init Polymer Fraction" in param_Fiber:
                    self.w30  = param_Fiber['Init Polymer Fraction']
                if "Init Solvent Fraction" in param_Fiber:
                    self.w20  = param_Fiber['Init Solvent Fraction']
                if "Init Non-Solvent Fraction" in param_Fiber:
                    self.w10  = param_Fiber['Init Non-Solvent Fraction']
                if "Inner Diameter" in param_Fiber:
                    self.di   = param_Fiber['Inner Diameter']
                if "Outer Diameter" in param_Fiber:
                    self.do   = param_Fiber['Outer Diameter']
            if "Coagulation Bath" in param:
                param_CB = param['Coagulation Bath']
                if "Temperature" in param_CB:
                    self.T_B  = param_CB['Temperature']
                if "Polymer Fraction" in param_CB:
                    self.w3_B = param_CB['Polymer Fraction']
                if "Solvent Fraction" in param_CB:
                    self.w2_B = param_CB['Solvent Fraction']
                if "Non-Solvent Fraction" in param_CB:
                    self.w1_B = param_CB['Non-Solvent Fraction']
            if "Other Conditions" in param:
                param_OC = param['Other Conditions']
                self.v   = param_OC['Spinning Speed']
            if "Physical Properties" in param:
                param_PP = param['Physical Properties']
                # self.rhoair = param_PP['Dry Air']['Density']
                # エアギャップ部の温度を基に乾燥空気の密度を計算
                self.rhoair = (self.P_AG/760 * 101325) / (R/Mair) / (self.T_AG+273.15) * 0.001
                self.rho2   = param_PP['Solvent']['Density']
                self.M2     = param_PP['Solvent']['Molecular Weight']
                self.rho1   = param_PP['Non-Solvent']['Density']
                self.M1     = param_PP['Non-Solvent']['Molecular Weight']
                self.rho    = param_PP['Dope']['Density']
            if "Transport Properties" in param:
                param_TP = param['Transport Properties']
                try:
                    self.uB    = param_TP['Air Velocity on Coagulation Bath']
                except Exception as e:
                    print(e)
                self.k_f   = param_TP['Mass Transfer AG to Fiber Surface']
                self.k_B   = param_TP['Mass Transfer CB to AG']
                self.delta = param_TP['Diffusion Film Thickness']


        except Exception as e:
            print('変数に問題があります.', file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(1)
        return param

    @property
    def L_AG(self) -> float:
        return self.__L_AG

    @property
    def d_AG(self) -> float:
        return self.__d_AG

    @property
    def T_AG(self) -> float:
        return self.__T_AG

    @property
    def P_AG(self) -> float:
        return self.__P_AG

    @property
    def w30(self) -> float:
        return self.__w30

    @property
    def w20(self) -> float:
        return self.__w20

    @property
    def w10(self) -> float:
        return self.__w10

    @property
    def di(self) -> float:
        return self.__di

    @property
    def do(self) -> float:
        return self.__do

    @property
    def T_B(self) -> float:
        return self.__T_B

    @property
    def w3_B(self) -> float:
        return self.__w3_B

    @property
    def w2_B(self) -> float:
        return self.__w2_B

    @property
    def w1_B(self) -> float:
        return self.__w1_B

    @property
    def v(self) -> float:
        return self.__v

    @property
    def rho2(self) -> float:
        return self.__rho2

    @property
    def M2(self) -> float:
        return self.__M2

    @property
    def rho1(self) -> float:
        return self.__rho1

    @property
    def M1(self) -> float:
        return self.__M1

    @property
    def rho(self) -> float:
        return self.__rho

    @property
    def uB(self) -> float:
        return self.__uB

    @property
    def k_f(self) -> float:
        return self.__k_f

    @property
    def k_B(self) -> float:
        return self.__k_B

    @property
    def delta(self) -> float:
        return self.__delta

    @L_AG.setter
    def L_AG(self, val: float):
        self.current_param['Air Gap']['Length'] = val
        self.__L_AG = val

    @d_AG.setter
    def d_AG(self, val: float):
        self.current_param['Air Gap']['Diameter'] = val
        self.__d_AG = val

    @T_AG.setter
    def T_AG(self, val: float):
        self.current_param['Air Gap']['Temperature'] = val
        self.__T_AG = val

    @P_AG.setter
    def P_AG(self, val: float):
        self.current_param['Air Gap']['Pressure'] = val
        self.__P_AG = val

    @w30.setter
    def w30(self, val: float):
        self.current_param['Fiber']['Init Polymer Fraction'] = val
        self.__w30 = val

    @w20.setter
    def w20(self, val: float):
        self.current_param['Fiber']['Init Solvent Fraction'] = val
        self.__w20 = val

    @w10.setter
    def w10(self, val: float):
        self.current_param['Fiber']['Init Non-Solvent Fraction'] = val
        self.__w10 = val

    @di.setter
    def di(self, val: float):
        self.current_param['Fiber']['Inner Diameter'] = val
        self.__di = val

    @do.setter
    def do(self, val: float):
        self.current_param['Fiber']['Outer Diameter'] = val
        self.__do = val

    @T_B.setter
    def T_B(self, val: float):
        self.current_param['Coagulation Bath']['Temperature'] = val
        self.__T_B = val

    @w3_B.setter
    def w3_B(self, val: float):
        self.current_param['Coagulation Bath']['Polymer Fraction'] = val
        self.__w3_B = val

    @w2_B.setter
    def w2_B(self, val: float):
        self.current_param['Coagulation Bath']['Solvent Fraction'] = val
        self.__w2_B = val

    @w1_B.setter
    def w1_B(self, val: float):
        self.current_param['Coagulation Bath']['Non-Solvent Fraction'] = val
        self.__w1_B = val

    @v.setter
    def v(self, val: float):
        self.current_param['Other Conditions']['Spinning Speed'] = val
        self.__v = val

    @rho2.setter
    def rho2(self, val: float):
        self.current_param['Physical Properties']['Solvent']['Density'] = val
        self.__rho2 = val

    @M2.setter
    def M2(self, val: float):
        self.current_param['Physical Properties']['Solvent']['Molecular Weight'] = val
        self.__M2 = val

    @rho1.setter
    def rho1(self, val: float):
        self.current_param['Physical Properties']['Non-Solvent']['Density'] = val
        self.__rho1 = val

    @M1.setter
    def M1(self, val: float):
        self.current_param['Physical Properties']['Non-Solvent']['Molecular Weight'] = val
        self.__M1 = val

    @rho.setter
    def rho(self, val: float):
        self.current_param['Physical Properties']['Dope']['Density'] = val
        self.__rho = val

    @uB.setter
    def uB(self, val: float):
        self.current_param['Transport Properties']['Air Velocity on Coagulation Bath'] = val
        self.__uB = val

    @k_f.setter
    def k_f(self, val: float):
        self.current_param['Transport Properties']['Mass Transfer AG to Fiber Surface'] = val
        self.__k_f = val

    @k_B.setter
    def k_B(self, val: float):
        self.current_param['Transport Properties']['Mass Transfer CB to AG'] = val
        self.__k_B = val

    @delta.setter
    def delta(self, val: float):
        self.current_param['Transport Properties']['Diffusion Film Thickness'] = val
        self.__delta = val

        
    def readParamFile(self, file_path: str) -> dict:
        """吸湿量計算に必要なパラメータを読み込む
           現在YAML, JSON形式のファイルに対応している

        Args:
            file_path (str): パラメータファイルのパス

        Returns:
            dict: 読み込んだパラメータ
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                extension = file_path.split(".")[-1]
                if extension in ["yaml", "yml"]: # YAML形式のファイルの場合
                    param = yaml.safe_load(file)
                elif extension in ["json"]:
                    param = json.load(file) # JSON形式のファイルの場合
                else:
                    print("対応しない拡張子です. ", file = sys.stderr)
        except Exception as e:
            print('ファイルパスを確認してください. ', file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(1)
        return self.readParam(param)

    def A_B(self) -> float:
        """凝固浴水面の面積を返す

        Returns:
            float: m2
        """
        return 0.25 * np.pi * (self.d_AG**2 - self.do**2)

    def P1sat(self) -> float:
        """エアギャップの飽和蒸気圧を返す
           (Tetensの式 1930)

        Returns:
            float: mmHg
        """
        # エアギャップの温度で計算
        return self.P_AG / 1013.25 * \
               (6.1078 * np.power(10, 7.5 * self.T_AG / (self.T_AG + 237.3)))
        # 凝固浴温度で計算
        # return self.P_AG / 1013.25 * \
        #        (6.1078 * np.power(10, 7.5 * self.T_B / (self.T_B + 237.3)))

    def D_AG(self) -> float:
        """エアギャップ中における水蒸気の拡散係数を返す

        Returns:
            float: m2/Hr
        """
        return 0.241 * np.power((self.T_AG + 273.15) / 288, 1.75) \
               * (760 / self.P_AG) * 1e-04 * 3600

    def C(self) -> float:
        """無次元中間変数

        Returns:
            float: 
        """
        return np.sqrt(self.k_f * np.pi * self.do / (self.rhoair * self.A_B() * self.D_AG()))

    def P1_B(self) -> float:
        """凝固浴水面における蒸気圧
           ラウール則を用いてP1satから算出

        Returns:
            float: 単位はself.P1satに同じ
        """
        ratio1 = self.w1_B / self.M1
        ratio2 = self.w2_B / self.M2
        # print(f"P1sat={self.P1sat()}")
        return  ratio1 / (ratio1 + ratio2) * self.P1sat()

    def HH_B(self) -> float:
        """凝固浴と平衡状態にある気相の絶対湿度

        Returns:
            float: kg-水蒸気 / kg-乾燥空気
        """
        # print(f"P1B = {self.P1_B()}")
        # print(f"VHHB = {self.rhoair*1000*18/29 * self.P1_B() / (self.P_AG - self.P1_B())}")
        return Mw/Mair * self.P1_B() / (self.P_AG - self.P1_B())

    def dmdt0(self) -> float:
        """糸の質量流量

        Returns:
            float: kg/hr
        """
        return self.rho * self.v * 60 * 0.25 * np.pi * \
               (self.do**2 - self.di**2)

    def dm1dt0(self) -> float:
        """

        Returns:
            float: _description_
        """
        return self.dmdt0() * self.w10

    def dm2dt0(self) -> float:
        return self.dmdt0() * self.w20

    def dm3dt0(self) -> float:
        return self.dmdt0() * self.w30

    def dm1dt(self, z: float = None) -> float:
        if isinstance(z, type(None)):
            return self.dm1dt(self.L_AG)
        return self.Psi1(z) * (self.dm2dt0() + self.dm3dt0())

    def H_AG(self, z: float = None) -> float:
        """AG部位置zに於ける重量絶対湿度を返す

        Args:
            z (float): AG部糸搬送方向の位置

        Returns:
            float: kg-水蒸気 / kg-乾燥空気
        """
        if isinstance(z, type(None)):
            return self.H_AG(self.L_AG)
        Cz   = self.C() * z
        CL   = self.C() * self.L_AG
        coef_m = 1. - self.rhoair * self.D_AG() * self.C() / self.k_B 
        coef_p = 1. + self.rhoair * self.D_AG() * self.C() / self.k_B 

        # return self.HH_B() * (np.exp(Cz) + np.exp(-Cz)) \
        #       / (coef_m * np.exp(CL) + coef_p * np.exp(-CL))
        #20230407プラスマイナス逆転修正
        return self.HH_B() * (np.exp(Cz) + np.exp(-Cz)) \
              / (coef_p * np.exp(CL) + coef_m * np.exp(-CL))

    def int_H_AG(self, z: float = None) -> float:
        """AG部位置zに於ける重量絶対湿度の積分値(0~z)を返す

        Args:
            z (float): AG部糸搬送方向の位置

        Returns:
            float: 
        """
        if isinstance(z, type(None)):
            return self.H_AG(self.L_AG)
        Cz   = self.C() * z
        CL   = self.C() * self.L_AG
        coef_m = 1. - self.rhoair * self.D_AG() * self.C() / self.k_B 
        coef_p = 1. + self.rhoair * self.D_AG() * self.C() / self.k_B 

        return self.HH_B() * (np.exp(Cz) - np.exp(-Cz)) \
              / (coef_p * np.exp(CL) + coef_m * np.exp(-CL)) / self.C()

    def VH_AG(self, z: float = None) -> float:
        """AG部位置zに於ける容積絶対湿度を返す

        Args:
            z (float, optional): AGにおける位置. Defaults to None.

        Returns:
            float: 容積絶対湿度 g/m3
        """
        return self.rhoair * 1000 * self.H_AG(z)

    def Psi1(self, z: float = None) -> float:
        """糸の位置zに於ける修正された貧溶媒重量分率を返す

        Args:
            z (float): 糸搬送方向の位置

        Returns:
            float: wt-ratio / wt-ratio
        """
        if isinstance(z, type(None)):
            return self.Psi1(self.L_AG)
        return self.k_f * np.pi * self.do / self.dmdt0() * self.int_H_AG(z)

    def ww1(self, z: float = None) -> float:
        """中空糸境膜における貧溶媒重量分率

        Args:
            z (float): 糸搬送方向の位置

        Returns:
            float: -
        """
        if isinstance(z, type(None)):
            return self.ww1(self.L_AG)
        return self.dm1dt(z) / \
               (
                self.dm1dt(z) + 
                (self.dm2dt0() + self.dm3dt0()) \
             * (self.do**2 - (self.do - self.delta)**2)
             / (self.do**2 - self.di**2) \
                ) 

    def ww2(self, z: float = None) -> float:
        """中空糸境膜における良溶媒重量分率

        Args:
            z (float): 糸搬送方向の位置

        Returns:
            float: -
        """
        if isinstance(z, type(None)):
            return self.ww1(self.L_AG)
        return self.dm2dt0() \
             * (self.do**2 - (self.do - self.delta)**2) \
             / (self.do**2 - self.di**2) \
             /  (
                self.dm1dt(z) + 
                (self.dm2dt0() + self.dm3dt0()) \
             * (self.do**2 - (self.do - self.delta)**2)
             / (self.do**2 - self.di**2) \
                ) 
    
    def ww3(self, z: float = None) -> float:
        """中空糸境膜におけるポリマー重量分率

        Args:
            z (float): 糸搬送方向の位置

        Returns:
            float: -
        """
        if isinstance(z, type(None)):
            return self.ww1(self.L_AG)
        return self.dm3dt0() \
             * (self.do**2 - (self.do - self.delta)**2) \
             / (self.do**2 - self.di**2) \
             /  (
                self.dm1dt(z) + 
                (self.dm2dt0() + self.dm3dt0()) \
             * (self.do**2 - (self.do - self.delta)**2)
             / (self.do**2 - self.di**2) \
                ) 

    def surfaceFraction(self, z: float = None) -> list:
        """中空糸境膜における重量分率組成

        Args:
            z (float): 糸搬送方向の位置

        Returns:
            float: -
        """
        if isinstance(z, type(None)):
            return self.ww1(self.L_AG), self.ww2(self.L_AG), self.ww3(self.L_AG)
        return self.ww1(z), self.ww2(z), self.ww3(z)

    def t(self, z: float = None) -> float:
        """紡口から吐出されzに到達するまでの時間

        Args:
            z (float, optional): _description_. Defaults to None.

        Returns:
            float: [s]
        """
        if isinstance(z, type(None)):
            return self.t(self.L_AG)
        return z / (self.v / 60)

    def plotVH_AG(self, ax: plt.Axes) -> plt.Axes:
        z = np.linspace(0, self.L_AG, 50)
        ax.plot(z, self.VH_AG(z))
        return ax

    def showVH_AG(self, point: float = None, save_path: str = None):
        """エアギャップ部における容積絶対湿度の分布をグラフに出力する

        Args:
            point (float, optional): 紡口からpointだけ離れたところの湿度をテキストでグラフに表示する. Defaults to None.
        """
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.set_xlabel("紡口面からの距離 $z$ [m]")
        ax.set_ylabel("容積絶対湿度 VH [g/m$^3$]")
        ax.tick_params(direction="in", top=True, bottom=True, left=True, right=True)
        ax.grid()
        ax.set_axisbelow(True)
        ax = self.plotVH_AG(ax)
        if not isinstance(point, type(None)):
            assert(point >=0 and point <= self.L_AG)
            y = self.VH_AG(point)
            ax.scatter(point, y, s = 100, color = "red")
            ax.annotate("{:.2f}".format(y), (point,y*1.05), color = "red")
        ax.set_xlim([0, 0.08])
        ax.set_ylim([0, 120])
        if not isinstance(save_path, type(None)):
            plt.savefig(save_path, dpi = 300, transparent=True)
        plt.show()
    
    def exportAllVariables(self, export_file_path: str = sys.stdout):
        """計算に用いる変数を出力する

        Args:
            export_file_path (str, optional): 出力するファイルのパス. Defaults to sys.stdout.
        """
        try:
            f = open(export_file_path, 'w', encoding='utf-8')
            print("エアギャップ条件", file=f)
            print("L_AG       = {:.2f} [mm]".format(self.L_AG*1000), file=f)
            print("d_AG       = {:.2f} [mm]".format(self.d_AG*1000), file=f)
            print("T_AG       = {:.1f} [℃]".format(self.T_AG), file=f)
            print("P_AG       = {:.2f} [mmHg]".format(self.P_AG), file=f)
            print("原液吐出条件", file=f)
            print("w_10       = {:.3f} [-]".format(self.w10), file=f)
            print("w_20       = {:.3f} [-]".format(self.w20), file=f)
            print("w_30       = {:.3f} [-]".format(self.w30), file=f)
            print("di         = {:.3f} [mm]".format(self.di*1000), file=f)
            print("do         = {:.3f} [mm]".format(self.do*1000), file=f)
            print("v          = {:.2f} [m/min]".format(self.v), file=f)
            print("凝固浴条件", file=f)
            print("T_B        = {:.2f} [℃]".format(self.T_B), file=f)
            print("w_1B       = {:.3f} [-]".format(self.w1_B), file=f)
            print("w_2B       = {:.3f} [-]".format(self.w2_B), file=f)
            print("w_3B       = {:.3f} [-]".format(self.w3_B), file=f)
            print("物性値", file=f)
            print("rhoair     = {:.3f} [kg/m3]".format(self.rhoair), file=f)
            print("rho2       = {:.3f} [kg/m3]".format(self.rho2), file=f)
            print("rho        = {:.3f} [kg/m3]".format(self.rho), file=f)
            print("M1         = {}     [g/mol]".format(self.M1), file=f)
            print("M2         = {}     [g/mol]".format(self.M2), file=f)
            print("物質移動パラメータ", file=f)
            print("k_f        = {:.2f} [kg/m2/hr]".format(self.k_f), file=f)
            print("k_B        = {:.2f} [kg/m2/hr]".format(self.k_B), file=f)
            print("delta      = {:.1f} [um]".format(self.delta*1000000), file=f)
            print("中間変数", file=f)
            print("A_B        = {:.2f} [mm2]".format(self.A_B()*1e+6), file=f)
            print("P1sat      = {:.2f} [mmHg]".format(self.P1sat()), file=f)
            print("D_AG       = {:.3e} [m2/hr]".format(self.D_AG()), file=f)
            print("C          = {:.3f} [-]".format(self.C()), file=f)
            print("P1_B       = {:.2f} [mmHg]".format(self.P1_B()), file=f)
            print("HH_B       = {:.3e} [kg/kg]".format(self.HH_B()), file=f)
            print("dmdt0      = {:.3e} [kg/hr]".format(self.dmdt0()), file=f)
            print("H_AG(L_AG) = {:.3e} [kg/kg]".format(self.H_AG(self.L_AG)), file=f)
            print("VH_AG(L_AG)= {:.3e} [g/m3]".format(self.VH_AG(self.L_AG)), file=f)
            print("Psi(L_AG)  = {:.5f} [-]".format(self.Psi1(self.L_AG)), file=f)
            print("ww1(L_AG)  = {:.5f} [-]".format(self.ww1(self.L_AG)), file=f)
            print("ww2(L_AG)  = {:.5f} [-]".format(self.ww2(self.L_AG)), file=f)
            print("ww3(L_AG)  = {:.5f} [-]".format(self.ww3(self.L_AG)), file=f)
            print("t(L_AG)    = {:.3e} [s]".format(self.t(self.L_AG)), file=f)
            print("uB approx  = {:.2f} [m/s]".format(self.uB), file=f)
            print("kB approx  = {:.2f} [kg/hr]".format(self.k_B_approx()), file=f)
            print("kf approx  = {:.2f} [kg/hr]".format(self.k_f_approx()), file=f)
            print("ShB        = {:.2f} [-]".format(self.ShB()), file=f)
            print("Shf        = {:.2f} [-]".format(self.Shf()), file=f)
            print("Sc         = {:.3e} [-]".format(self.Sc()), file=f)
            print("ReB        = {:.2f} [-]".format(self.ReB()), file=f)
            print("Ref        = {:.2f} [-]".format(self.Ref()), file=f)
            print("mu         = {:.3e} [Pa･s]".format(self.muair()), file=f)
            f.close()
        except Exception as e:
            print(e, file=sys.stderr)
            print("設定されていない変数がある可能性があります. ")

    def k_B_approx(self) -> float:
        """k_Bの推算値
           シャーウッド数定義式を変形して得られたもの

        Returns:
            float: k_Bの値 [kg/hr]
        """
        return self.ShB() * self.D_AG() * self.rhoair / self.d_AG

    def k_f_approx(self) -> float:
        """k_fの推算値
           シャーウッド数定義式を変形して得られたもの

        Returns:
            float: k_fの値 [kg/hr]
        """
        return self.Shf() * self.D_AG() * self.rhoair / self.do

    def Shf(self) -> float:
        """糸表面におけるシャーウッド数を返す
           J.Welty, C.E.Wicks, G.L.Rorrer , R.E.Wilson, 
           Fundamentals of Momentum, Heat and Mass Transfer 
           5th Edition, Wiley, 2007, p. p.581.

        Returns:
            float: 糸表面におけるシャーウッド数 [-]
        """
        Ref = self.Ref()
        if Ref < 10 or Ref >= 35000:
            raise Exception(f"Re={Ref}適用範囲外のレイノルズ数です")
        if Ref < 2000:
            return 1.86 * Ref**(1/3) * self.Sc()**(1/3) \
                   * (self.do / self.L_AG)**(1/3)
        else:
            return 0.023 * Ref**(0.83) * self.Sc()**(0.44) 

    def ShB(self) -> float:
        """凝固浴界面におけるシャーウッド数を返す
           Sherwood (1975)

        Returns:
            float: 凝固浴面におけるシャーウッド数 [-]
        """
        if self.ReB() < 0 or self.ReB() >= 2.e+5:
            raise Exception(f"Re={self.ReB()}適用範囲外のレイノルズ数です")
        return 0.332 * self.ReB()**(1/2) * self.Sc()**(1/3)


    def ReB(self) -> float :
        """凝固浴面におけるレイノルズ数を返す

        Returns:
            float: 凝固浴面におけるレイノルズ数 [-]
        """
        return self.rhoair * self.uB * self.d_AG / self.muair()

    def Ref(self) -> float :
        """糸表面におけるレイノルズ数を返す

        Returns:
            float: 糸表面におけるレイノルズ数 [-]
        """
        return self.rhoair * (self.v/60) * self.do / self.muair()

    def Sc(self) -> float:
        """凝固浴面におけるシュミット数を返す

        Returns:
            float: 凝固浴面におけるシュミット数 [-]
        """
        return self.muair() / self.rhoair / (self.D_AG() / 3600)

    def muair(self) -> float:
        """T_AGに於ける乾燥空気の粘度
           Sutherland (1893)

        Returns:
            float: [Pa･s]
        """
        T_K = self.T_AG + 273.15
        return 1.458e-6 * T_K**(3/2) / (T_K + 110.4)

    # def frac1(self, z: float = None):
    #     if isinstance(z, type(None)):
    #         return self.frac1(self.L_AG)
    #     Cz   = self.C() * z
    #     return self.HH_B() * (np.exp(Cz) + np.exp(-Cz)) 

    # def frac2(self, z: float = None):
    #     if isinstance(z, type(None)):
    #         return self.frac2(self.L_AG)
    #     Cz   = self.C() * z
    #     CL   = self.C() * self.L_AG
    #     coef_m = 1. - self.rhoair * self.D_AG() * self.C() / self.k_B 
    #     coef_p = 1. + self.rhoair * self.D_AG() * self.C() / self.k_B 
    #     return (coef_m * np.exp(CL) + coef_p * np.exp(-CL))

    # def coef1(self):
    #     return 1. - self.rhoair * self.D_AG() * self.C() / self.k_B 
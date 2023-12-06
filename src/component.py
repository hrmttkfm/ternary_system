class Component:
    """成分を表すクラス
    """
    def __init__(self, nu: float, rho: float, name: str = ""):
        """コンストラクタ

        Args:
            nu (float): 成分のモル体積
            rho (float): 成分の密度
            name (str): 成分の名前
        """
        self.name = name # 成分名
        self.nu   = nu   # 成分のモル体積
        self.rho  = rho  # 純成分である場合の密度
        self.phi  = 0.   # 体積分率
    
    def copy(self):
        """オブジェクトのコピー関数

        Returns:
            Component: Componentオブジェクト
        """
        obj_copy = Component(self.nu, self.rho, self.name)
        obj_copy.phi = self.phi
        return obj_copy

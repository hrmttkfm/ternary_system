# 過剰混合ギブズエネルギーデータから貧溶媒・溶媒間相互作用パラメータg12を推定する
import sys
sys.path.append(r"src")
from component import Component
from phase import Phase

R = 8.31446262 # m2 kg s-2 K-1 mol-1 気体定数
if __name__ == "__main__":
    # PSF/NMP/水系
    n_solvent = Component(18   , 1.  , "Water")
    solvent   = Component(71.29, 1.03, "NMP"  )
    polymer   = Component(20270, 1.24, "PSF"  )

    phase_init = Phase(n_solvent, solvent, polymer, 0.,0.,0.)

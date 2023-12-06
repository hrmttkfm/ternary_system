import unittest
import sys
sys.path.append(r"src")
from VIPS import VIPS

param_dict = {
    "Air Gap": {
        "Length": 0.3,
        "Diameter": 0.03,
        "Temperature": 56,
        "Pressure": 760
    },
    "Fiber": {
        "Init Polymer Fraction": 0.38,
        "Init Solvent Fraction": 0.62,
        "Init Non-Solvent Fraction": 0,
        "Inner Diameter": 5.5e-04,
        "Outer Diameter": 1.15e-03
    },
    "Coagulation Bath": {
        "Temperature": 27,
        "Polymer Fraction": 0,
        "Solvent Fraction": 0,
        "Non-Solvent Fraction": 1
    },
    "Other Conditions": {
        "Spinning Speed": 20
    },
    "Physical Properties": {
        "Dry Air": {
            "Density": 1.073
        },
        "Solvent": {
            "Density": 1030,
            "Molecular Weight": 99.13
        },
        "Non-Solvent": {
            "Density": 1000,
            "Molecular Weight": 18
        },
        "Dope": {
            "Density": 1185
        }
    },
    "Transport Properties": {
        "Mass Transfer AG to Fiber Surface": 100,
        "Mass Transfer CB to AG": 50,
        "Diffusion Film Thickness": 3.0e-06
    }
}


class TestVIPS1(unittest.TestCase):
    def setUp(self):
        self.vips = VIPS()
        self.vips.readParamFile(f"tests\params_VIPS.yaml")

    def test_A_B(self):
        A_B = self.vips.A_B()
        print("A_B = ", A_B)
        self.assertTrue(abs(A_B - 7.06e-04) < 1e-05)

    def test_D_AG(self):
        D_AG = self.vips.D_AG()
        print("D_AG = ", D_AG)
        self.assertTrue(abs(D_AG - 3.04452e-05 * 3600) < 1e-06)

    def test_rhoAD(self):
        rhoAD = self.vips.rhoair * self.vips.A_B() * self.vips.D_AG()
        print("rhoAD = ", rhoAD)
        self.assertTrue(abs(rhoAD - 8.3e-05) < 1e-05)

    def test_C(self):
        C = self.vips.C()
        print("C = ", C)
        self.assertTrue(abs(C - 66) < 1)

    def test_P1sat(self):
        P1sat = self.vips.P1sat()
        print("P1sat = ", P1sat)
        self.assertTrue(abs(P1sat - 123.9) < 1)

    def test_P1_B(self):
        P1_B = self.vips.P1_B()
        print("P1_B = ", P1_B)
        self.assertTrue(abs(P1_B - 123.9) < 1)

    def test_dm2dt0(self):
        dm2dt0 = self.vips.dm2dt0()
        print("dm2dt0 = ", dm2dt0)
        self.assertTrue(abs(dm2dt0 - 0.706) < 0.01)

    def test_HH_B(self):
        HH_B = self.vips.HH_B()
        print("HH_B = ", HH_B)
        self.assertTrue(abs(HH_B - 0.1209) < 0.01)

    def test_t(self):
        t = self.vips.t()
        print("t = ", t)
        self.assertTrue(abs(t - 0.9) < 0.01)

    def test_end_H_AG(self):
        H_AG = self.vips.H_AG()
        print("H_AG = ", H_AG)
        self.assertTrue(abs(H_AG - 1.43e-01) < 1e-03)

    def test_end_Psi(self):
        Psi1 = self.vips.Psi1()
        print("Psi1 = ", Psi1)
        self.assertTrue(abs(Psi1 - 6.88e-04) < 1e-06)

    def test_end_ww1(self):
        ww1 = self.vips.ww1()
        print("ww1  = ", ww1)
        self.assertTrue(abs(ww1 - 9.24 * 0.01) < 1e-02)

class TestVIPS2(unittest.TestCase):
    def setUp(self):
        self.vips = VIPS()
        self.vips.readParam(param_dict)

    def test_A_B(self):
        A_B = self.vips.A_B()
        print("A_B = ", A_B)
        self.assertTrue(abs(A_B - 7.06e-04) < 1e-05)

    def test_D_AG(self):
        D_AG = self.vips.D_AG()
        print("D_AG = ", D_AG)
        self.assertTrue(abs(D_AG - 3.04452e-05 * 3600) < 1e-06)

    def test_rhoAD(self):
        rhoAD = self.vips.rhoair * self.vips.A_B() * self.vips.D_AG()
        print("rhoAD = ", rhoAD)
        self.assertTrue(abs(rhoAD - 8.3e-05) < 1e-05)

    def test_C(self):
        C = self.vips.C()
        print("C = ", C)
        self.assertTrue(abs(C - 66) < 1)

    def test_P1sat(self):
        P1sat = self.vips.P1sat()
        print("P1sat = ", P1sat)
        self.assertTrue(abs(P1sat - 123.9) < 1)

    def test_P1_B(self):
        P1_B = self.vips.P1_B()
        print("P1_B = ", P1_B)
        self.assertTrue(abs(P1_B - 123.9) < 1)

    def test_dm2dt0(self):
        dm2dt0 = self.vips.dm2dt0()
        print("dm2dt0 = ", dm2dt0)
        self.assertTrue(abs(dm2dt0 - 0.706) < 0.01)

    def test_HH_B(self):
        HH_B = self.vips.HH_B()
        print("HH_B = ", HH_B)
        self.assertTrue(abs(HH_B - 0.1209) < 0.01)

    def test_t(self):
        t = self.vips.t()
        print("t = ", t)
        self.assertTrue(abs(t - 0.9) < 0.01)

    def test_end_H_AG(self):
        H_AG = self.vips.H_AG()
        print("H_AG = ", H_AG)
        self.assertTrue(abs(H_AG - 1.43e-01) < 1e-03)

    def test_end_Psi(self):
        Psi1 = self.vips.Psi1()
        print("Psi1 = ", Psi1)
        self.assertTrue(abs(Psi1 - 6.88e-04) < 1e-06)

    def test_end_ww1(self):
        ww1 = self.vips.ww1()
        print("ww1  = ", ww1)
        self.assertTrue(abs(ww1 - 9.24 * 0.01) < 1e-02)

class TestVIPS3(unittest.TestCase):
    def setUp(self):
        self.vips = VIPS()
        self.vips.readParamFile(f"tests\params_VIPS.json")

    def test_A_B(self):
        A_B = self.vips.A_B()
        print("A_B = ", A_B)
        self.assertTrue(abs(A_B - 7.06e-04) < 1e-05)

    def test_D_AG(self):
        D_AG = self.vips.D_AG()
        print("D_AG = ", D_AG)
        self.assertTrue(abs(D_AG - 3.04452e-05 * 3600) < 1e-06)

    def test_rhoAD(self):
        rhoAD = self.vips.rhoair * self.vips.A_B() * self.vips.D_AG()
        print("rhoAD = ", rhoAD)
        self.assertTrue(abs(rhoAD - 8.3e-05) < 1e-05)

    def test_C(self):
        C = self.vips.C()
        print("C = ", C)
        self.assertTrue(abs(C - 66) < 1)

    def test_P1sat(self):
        P1sat = self.vips.P1sat()
        print("P1sat = ", P1sat)
        self.assertTrue(abs(P1sat - 123.9) < 1)

    def test_P1_B(self):
        P1_B = self.vips.P1_B()
        print("P1_B = ", P1_B)
        self.assertTrue(abs(P1_B - 123.9) < 1)

    def test_dm2dt0(self):
        dm2dt0 = self.vips.dm2dt0()
        print("dm2dt0 = ", dm2dt0)
        self.assertTrue(abs(dm2dt0 - 0.706) < 0.01)

    def test_HH_B(self):
        HH_B = self.vips.HH_B()
        print("HH_B = ", HH_B)
        self.assertTrue(abs(HH_B - 0.1209) < 0.01)

    def test_t(self):
        t = self.vips.t()
        print("t = ", t)
        self.assertTrue(abs(t - 0.9) < 0.01)

    def test_end_H_AG(self):
        H_AG = self.vips.H_AG()
        print("H_AG = ", H_AG)
        self.assertTrue(abs(H_AG - 1.43e-01) < 1e-03)

    def test_end_Psi(self):
        Psi1 = self.vips.Psi1()
        print("Psi1 = ", Psi1)
        self.assertTrue(abs(Psi1 - 6.88e-04) < 1e-06)

    def test_end_ww1(self):
        ww1 = self.vips.ww1()
        print("ww1  = ", ww1)
        self.assertTrue(abs(ww1 - 9.24 * 0.01) < 1e-02)

    def test_end_fraction(self):
        ww1, ww2, ww3 = self.vips.surfaceFraction()
        print("total frac = ", ww1 + ww2 + ww3)
        self.assertAlmostEqual(ww1 + ww2 + ww3, 1.0)

if __name__ == "__main__":
    unittest.main()
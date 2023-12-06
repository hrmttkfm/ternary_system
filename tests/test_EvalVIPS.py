import unittest
import sys
sys.path.append(r"src")
from eval_VIPS import EvalVIPS

class TestVIPS1(unittest.TestCase):
    def setUp(self):
        self.evp = EvalVIPS()
        self.evp.setBinodalCurve(r"tests\binodalFitFunc.pkl")
        self.evp.setDefaultParam(f"tests\params_VIPS.yaml")
        # self.evp.setParamTable(f"tests\params_table.xlsx")

    def test_notVIPS(self):
        # VIPSが起きないパラメータでのテスト
        self.evp.vips.d_AG = 0.02
        _, _, deviation = self.evp.communicate()
        self.assertEqual(deviation, None)

    def test_okVIPS(self):
        # VIPSが起きるパラメータでのテスト
        self.evp.vips.d_AG = 0.05
        _, _, deviation = self.evp.communicate()
        self.assertNotEqual(deviation, None)
        print("deviation = {:.5f}".format(deviation))

    def test_paramTableCorrespondence(self):
        # param_tableを読み取り、それぞれのパラメータに対して
        # VIPSが起きるか否か、起きる場合はバイノーダルラインからの逸脱量を計算
        self.evp.setParamTable("tests\param_table.xlsx")
        fraction_init_list, fraction_list, deviation_list = self.evp.communicateLoop()
        self.assertEqual(deviation_list[0], None)
        self.assertEqual(deviation_list[1], None)
        self.assertEqual(deviation_list[2], None)
        self.assertEqual(deviation_list[3], None)
        self.assertEqual(deviation_list[4], None)
        self.assertEqual(deviation_list[5], None)
        self.assertEqual(deviation_list[6], None)
        self.assertEqual(deviation_list[7], None)
        self.assertEqual(deviation_list[8], None)
        self.assertAlmostEqual(deviation_list[9], 0.018740687523988865)
        self.assertEqual(deviation_list[10], None)
        self.assertAlmostEqual(deviation_list[11], 0.004838893571703887)
        self.assertAlmostEqual(deviation_list[12], 0.0012167742657699426)

if __name__ == "__main__":
    unittest.main()
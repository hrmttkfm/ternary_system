import sys
sys.path.append(r"src")
from eval_VIPS import EvalVIPS

if __name__ == "__main__":
    evp = EvalVIPS()
    evp.setBinodalCurve(r"tests\binodalFitFunc.pkl")
    evp.setDefaultParam(f"tests\params_VIPS.yaml")
    evp.setParamTable("tests\param_table.xlsx")
    fraction_list, deviation_list = evp.communicateLoop()

    evp.exportResultLoop("Psf+TEG", "NMP", "H2O", None, r"tests\test_visu.html")
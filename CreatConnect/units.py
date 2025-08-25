# units.py
CREATININE_MW_G_PER_MOL = 113.12

def mM_to_mg_dL(value_mM: float, mw_g_per_mol: float = CREATININE_MW_G_PER_MOL) -> float:
    # mg/dL = mM * MW / 10
    return float(value_mM) * (mw_g_per_mol / 10.0)

def mg_dL_to_mM(value_mg_dL: float, mw_g_per_mol: float = CREATININE_MW_G_PER_MOL) -> float:
    # mM = mg/dL * 10 / MW
    return float(value_mg_dL) * (10.0 / mw_g_per_mol)
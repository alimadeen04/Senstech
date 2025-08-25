import numpy as np

def movavg(x, k=5):
    if k <= 1 or len(x) < 3:
        return np.asarray(x, dtype=float)
    return np.convolve(x, np.ones(k)/k, mode="same")

def concentration_from_cv(V_volts, I_uA, calibrator, smooth_k=5, peak="reduction"):
    """
    peak: 'reduction' (most negative), 'oxidation' (most positive), or 'abs' (largest magnitude)
    Returns: (conc_out, Ip_uA, Vp_mV, peak_idx)
    """
    if len(V_volts) == 0 or len(I_uA) == 0:
        return None, None, None, None

    I_s = movavg(I_uA, k=smooth_k)

    if peak == "reduction":
        peak_idx = int(np.argmin(I_s))          # <-- most negative current
    elif peak == "oxidation":
        peak_idx = int(np.argmax(I_s))
    else:
        peak_idx = int(np.argmax(np.abs(I_s)))

    Ip_uA = float(I_s[peak_idx])
    Vp_mV = float(V_volts[peak_idx] * 1000.0)

    # calibrator already converts to target unit (mg/dL) if configured
    conc_out = calibrator.apply(Ip_uA)
    return conc_out, Ip_uA, Vp_mV, peak_idx



# calibration.py
import json, numpy as np
from units import mM_to_mg_dL, mg_dL_to_mM

class Calibrator:
    def __init__(self, path="calibration.json", target_unit=None):
        with open(path, "r") as f:
            cfg = json.load(f)
        self.kind = (cfg.get("type") or "linear").lower()
        self.coeffs = cfg.get("coeffs", [])
        self.x_unit = cfg.get("x_unit", "uA")
        self.y_unit = cfg.get("y_unit", "mM")             # model output unit
        self.target_unit = (target_unit or
                            cfg.get("target_unit", self.y_unit))
        self.decimals = cfg.get("decimals", 2)
        self.mw = cfg.get("mw_g_per_mol", 113.12)         # creatinine default
        lo, hi = cfg.get("valid_range_uA", [-1e9, 1e9])
        self.valid_lo, self.valid_hi = float(lo), float(hi)

        # inverse-specific options
        self.use_abs = bool(cfg.get("use_abs_current", False))
        self.x_offset = float(cfg.get("x_offset_uA", 0.0))
        self.min_abs = float(cfg.get("min_abs_uA", 1e-6))

    def apply(self, current_uA: float) -> float:
        # sanity/window check
        if not (self.valid_lo <= current_uA <= self.valid_hi):
            raise ValueError(f"Current {current_uA} uA outside valid range [{self.valid_lo}, {self.valid_hi}]")

        x = float(current_uA)
        if self.use_abs:
            x = abs(x)

        if self.kind == "linear":
            # y = b0 + b1*x
            b0, b1 = self._get_coeffs(2)
            y = b0 + b1 * x

        elif self.kind == "polynomial":
            # y = b0 + b1*x + b2*x^2 + ...
            # coeffs in JSON are [b0,b1,...]; np.polyval wants highest-first
            y = float(np.polyval(list(reversed(self.coeffs)), x))

        elif self.kind == "inverse":
            # y = b0 + k / (x - x0)
            # coeffs: [b0, k]  (if only one provided, interpret as [0, k])
            if len(self.coeffs) == 1:
                b0, k = 0.0, float(self.coeffs[0])
            else:
                b0, k = float(self.coeffs[0]), float(self.coeffs[1])

            denom = x - self.x_offset
            if abs(denom) < self.min_abs:
                raise ValueError(f"Current too close to zero for inverse model (|I - {self.x_offset}| < {self.min_abs} µA)")
            y = b0 + k / denom

        else:
            raise ValueError(f"Unknown calibration type: {self.kind}")

        # unit conversion (model y_unit -> desired target_unit)
        y_conv = self._convert_units(y, self.y_unit, self.target_unit)
        return float(round(y_conv, self.decimals))

    def _get_coeffs(self, n):
        if len(self.coeffs) < n:
            raise ValueError(f"{self.kind} requires {n} coeffs, got {len(self.coeffs)}")
        return [float(c) for c in self.coeffs[:n]]

    def _convert_units(self, val, src, dst):
        src = (src or "").lower()
        dst = (dst or "").lower()
        if src == dst or not dst:
            return val
        # handle mM <-> mg/dL for creatinine
        if src in ("mm", "mmol/l", "mmol", "mmol_l"):
            if dst in ("mg/dl", "mgdl", "mg_per_dl"):
                return mM_to_mg_dL(val, self.mw)
        if src in ("mg/dl", "mgdl", "mg_per_dl"):
            if dst in ("mm", "mmol/l", "mmol", "mmol_l"):
                return mg_dL_to_mM(val, self.mw)
        # extend if you ever support other units
        return val




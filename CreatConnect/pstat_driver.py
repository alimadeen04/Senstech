# pstat_driver.py
from potentiostat import Potentiostat

def run_cv_blocking(
    port: str,
    params: dict,
    curr_range: str = "100uA",
    sample_period_ms: int = 10,
    name: str = "cyclic",
    show_progress: bool = True,
):
    """Run a CV test and return (t, volt, curr)."""
    dev = Potentiostat(port)
    try:
        dev.set_curr_range(curr_range)
        dev.set_sample_period(sample_period_ms)
        dev.set_param(name, params)
        t, volt, curr = dev.run_test(name, display='pbar' if show_progress else None)
        return t, volt, curr
    finally:
        try:
            dev.close()
        except Exception:
            pass

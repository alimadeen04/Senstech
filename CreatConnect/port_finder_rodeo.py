# port_finder_rodeo.py
from serial.tools import list_ports
from potentiostat import Potentiostat

def find_rodeostat_port_by_device_id(target_id: int) -> str:
    """Return COM path for the Rodeostat with this device_id (e.g., 'COM5' or '/dev/ttyACM0')."""
    for info in list_ports.comports():
        try:
            p = Potentiostat(info.device)
            did = int(p.get_device_id())
            p.close()
            if did == int(target_id):
                return info.device
        except Exception:
            # Not a Rodeostat or busy: ignore and continue scanning
            pass
    raise RuntimeError(f"No Rodeostat with device_id={target_id} found.")

# CreatConnect

A Python desktop app for an electrochemical creatinine biosensor, built for Cornell SensTech. It runs a cyclic voltammetry (CV) measurement on a potentiostat, converts the peak current into a creatinine concentration, and reports the result against thresholds personalized to the user's age, sex, and weight.

> Prototype for a student engineering project. Not a medical device, and the thresholds are not clinical guidance.

## How it works

```
Rodeostat potentiostat ──► CV sweep (time, voltage, current)
        │
        ▼
Smoothing (moving average) ──► Peak detection (reduction, oxidation, or largest magnitude)
        │
        ▼
Calibration model (current in µA ──► concentration in mM ──► mg/dL)
        │
        ▼
Personalized status (Low / Normal / High) + explanation ──► graph, menu, history log
```

The app has two input modes:

- **Hardware mode** connects to an IO Rodeo Rodeostat over USB, finds the device by its ID, and runs the CV test on a background thread so the interface stays responsive.
- **Simulated mode** replays labeled CV curves from `simulated_data/` (low, normal, and high creatinine) so the app can be demonstrated without the sensor.

## Project structure

| File | Purpose |
| --- | --- |
| `main.py` | Entry point. Builds the screen manager and registers fonts. |
| `pstat_driver.py` | Runs a CV test on the potentiostat and returns time, voltage, and current. |
| `port_finder_rodeo.py` | Scans serial ports to find the Rodeostat with a given device ID. |
| `sensor_pipeline.py` | Smooths the current trace and extracts the peak current and peak potential. |
| `calibration.py` | Configurable calibration model (linear, polynomial, or inverse) with range checks and unit conversion. |
| `calibration.json` | Calibration coefficients and settings. Edit this to recalibrate without changing code. |
| `units.py` | Converts between mM and mg/dL using creatinine's molecular weight. |
| `personalization.py` | Sets Low / Normal / High thresholds from age, sex, and weight, and generates explanations. |
| `sensor_input.py` | Loads simulated CV data and the user's saved health profile. |
| `graph.py` | Live CV plot widget. |
| `user_interface.py` | Sensor screen. Connects the measurement, pipeline, and display. |
| `menu_screen.py`, `visual.py` | Home menu and results visualization. |
| `health_info_screen.py`, `history_log_screen.py` | Health profile entry and measurement history. |

## Running the app

Requires Python 3.8 or later.

```bash
git clone https://github.com/alimadeen04/Senstech.git
cd Senstech/CreatConnect
pip install -r requirements.txt
python main.py
```

Run it from inside `CreatConnect/`, since the app loads `calibration.json`, `health_info.json`, and the simulated data by relative path. Without a potentiostat connected, use the sensor screen to run a simulated reading.

## Calibration

`calibration.json` defines how peak current maps to concentration. Example (inverse model):

```json
{
  "type": "inverse",
  "coeffs": [0.0, -565.0],
  "y_unit": "mM",
  "target_unit": "mg/dL",
  "valid_range_uA": [-100, 100]
}
```

Supported models:

- `linear`: y = b0 + b1·x
- `polynomial`: y = b0 + b1·x + b2·x² + ...
- `inverse`: y = b0 + k / (x − x0)

Readings outside `valid_range_uA` raise an error instead of returning a misleading value.

## Contributions

Built by the Cornell SensTech dry lab team.

- **Alima Deen** (Dry Lab Software Lead): app architecture, potentiostat driver and port detection, CV signal processing and peak detection, calibration module and unit conversion, simulated data, personalization logic, sensor and graph screens.
- **Vinesha Shaik**: health info and history log screens, menu layout updates.

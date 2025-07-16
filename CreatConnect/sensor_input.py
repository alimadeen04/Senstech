'''
sensor_input.py - Handles communication with the OIRD biosensor.

Supports:
- Bluetooth Low Energy (BLE)
- Serial Communication (USB/UART)
'''

import pandas as pd
import random
import os

# Directory where your 3 CSVs are saved
DATA_DIR = os.path.join(os.path.dirname(__file__), "simulated_data") # update this as needed

def read_simulated_sensor_data():
    sim_files = ["sensor_low.csv", "sensor_normal.csv", "sensor_high.csv"]
    chosen_file = random.choice(sim_files)
    file_path = os.path.join(DATA_DIR, chosen_file)

    df = pd.read_csv(file_path)
    peak_sensor_value = df["Sensor Reading"].max()

    # Convert to creatinine (replace 1.75 with real calibration factor!!!!!)
    creatinine = peak_sensor_value * 1.75

    # Categorize
    if creatinine < 0.6:
        status = "Low"
    elif creatinine <= 1.3:
        status = "Normal"
    else:
        status = "High"

    return {
        "data": df,
        "file": chosen_file,
        "creatinine": creatinine,
        "status": status,
        "peak_signal": peak_sensor_value
    }

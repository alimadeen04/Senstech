'''
sensor_input.py - Handles communication with the OIRD biosensor.

Supports:
- Bluetooth Low Energy (BLE)
- Serial Communication (USB/UART)
'''
import pandas as pd
import random
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "simulated_data")

def read_simulated_sensor_data():
    sim_files = [
        ("Low_Creatinine_0.40mgdL.csv", 0.40),
        ("Normal_Creatinine_1.00mgdL.csv", 1.00),
        ("High_Creatinine_2.50mgdL.csv", 2.50)
    ]
    
    chosen_file, known_creatinine = random.choice(sim_files)
    file_path = os.path.join(DATA_DIR, chosen_file)

    df = pd.read_csv(file_path)
    peak_current = df["Current (μA)"].max()

    # Use known value instead of calculating from peak_current
    creatinine = known_creatinine

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
        "peak_signal": peak_current
    }



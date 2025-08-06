'''
sensor_input.py - Handles communication with the OIRD biosensor.

Supports:
- Bluetooth Low Energy (BLE)
- Serial Communication (USB/UART)
'''
import pandas as pd
import random
import os
import json  # You forgot to import json
from personalization import get_status, get_breakdown

def load_health_info():
    default = {'age': 30, 'weight': 70, 'gender': 'Female'}
    try:
        if os.path.exists('health_info.json'):
            with open('health_info.json', 'r') as f:
                data = json.load(f)
            return {
                'age': int(data.get('age', default['age'])),
                'weight': float(data.get('weight', default['weight'])),
                'gender': data.get('gender', default['gender'])
            }
    except Exception as e:
        print("Error loading health info:", e)
    return default

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

    # ✅ Use personalized thresholds
    user_info = load_health_info()
    status = get_status(creatinine, user_info['age'], user_info['gender'], user_info['weight'])

    return {
        "data": df,
        "file": chosen_file,
        "creatinine": creatinine,
        "status": status,
        "peak_signal": peak_current
    }




'''
sensor_input.py - Handles communication with the OIRD biosensor.

Supports:
- Bluetooth Low Energy (BLE)
- Serial Communication (USB/UART)
'''
import random


def read_sensor_data():
    """
    Simulates creatinine level from reflectivity.
    You can later replace this with real sensor reading logic (BLE or Serial).
    """
    reflectivity = random.uniform(0.1, 1.0)
    creatinine = round(0.5 + 1.5 * reflectivity, 2)
    return creatinine
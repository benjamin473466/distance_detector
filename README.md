# Distance Alert Project

This project uses a Raspberry Pi Pico to measure distances with an ultrasonic sensor, display the results on an I2C LCD, and alert when the measured distance is close to a setpoint using a buzzer. A potentiometer is used to adjust the setpoint.

## Hardware Setup

### Components:
- **Raspberry Pi Pico**
- **Ultrasonic Sensor (HC-SR04)**
- **I2C LCD (16x2)**
- **Buzzer**
- **Potentiometer**

### Pin Connections:
- **Ultrasonic Sensor**:
  - TRIG → GP3
  - ECHO → GP2
  - VCC → 3V3
  - GND → GND
- **I2C LCD**:
  - SDA → GP0
  - SCL → GP1
  - VCC → 3V3
  - GND → GND
- **Buzzer**:
  - Positive → GP4
  - Negative → GND
- **Potentiometer**:
  - Signal → GP26
  - VCC → 3V3
  - GND → GND

## Software Details

### Features:
1. **Distance Measurement**:
   - Uses the ultrasonic sensor to measure distance in centimeters.
   - Converts the distance to feet and inches for display.
2. **Setpoint Adjustment**:
   - The potentiometer adjusts the setpoint distance (0–20 feet).
3. **Alert System**:
   - The buzzer activates when the measured distance is within ~0.5 inches of the setpoint.
4. **Display**:
   - The I2C LCD shows the measured distance and the setpoint in feet and inches.

### Dependencies:
- `machine` (MicroPython module for hardware control)
- `utime` (MicroPython module for timing)
- `lcd_api` (Custom library for LCD control)
- `i2c_lcd` (Custom library for I2C LCD control)

### How to Run:
1. Upload the Python files (`distance_alert.py`, `lcd_api.py`, `i2c_lcd.py`) to the Pico.
2. Connect the hardware as per the pin connections.
3. Run the `distance_alert.py` script on the Pico.

### Notes:
- Ensure the MicroPython firmware is installed on the Pico.
- Adjust the I2C address in the code if your LCD uses a different address (default: `0x27`).

## Circuit Diagram
Refer to the JSON file for the simulated circuit setup in Wokwi.

Pico Project

This folder contains `main.py` for your Raspberry Pi Pico W.

Quick tasks (in VS Code):

- Run the upload task: Ctrl+Shift+P → Tasks: Run Task → select "Pico: Upload main.py". This runs:
  mpremote connect auto fs put "${workspaceFolder}/main.py" :/main.py

- Run the script on device: Ctrl+Shift+P → Tasks: Run Task → select "Pico: Run main.py". This runs:
  mpremote connect auto run :/main.py

If you want automatic upload on save, install the "Run on Save" extension (emeraldwalk.runonsave) and add a rule to run the upload task on save.

Install mpremote (if not already):

```powershell
python -m pip install --user mpremote
$env:Path += ";" + (python -m site --user-base) + "\Scripts"
mpremote --version
```

Notes:
- Use a USB data cable (not a charge-only cable).
- If `mpremote connect auto` fails, find the COM port in Device Manager and replace `auto` with the port (for example `COM3`).

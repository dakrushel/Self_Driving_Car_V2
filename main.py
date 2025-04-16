import threading
import tkinter as tk

# GUI
from GUI.MainWindow import DarkGUI

# Sensor Threads
try:
    from Controllers.GyroAccelerometerController import run as gyro_run_loop
    from Controllers.UltrasonicController import run as ultra_run_loop
    from Controllers.CameraController import run as camera_run  # Untested
    hardware_available = True
except ImportError as e:
    print("[main.py] WARNING: Some hardware modules not found.")
    print("[main.py] Details:", e)
    gyro_run_loop = None
    ultra_run_loop = None
    camera_run = None
    hardware_available = False


def start_sensor_threads():
    """Start sensor monitoring threads if hardware is available."""
    if gyro_run_loop:
        threading.Thread(target=gyro_run_loop, daemon=True).start()
        print("[main.py] Gyro thread started")

    if ultra_run_loop:
        threading.Thread(target=ultra_run_loop, daemon=True).start()
        print("[main.py] Ultrasonic thread started")

    if camera_run:
        # Optional: uncomment to auto-start camera
        # threading.Thread(target=camera_run, daemon=True).start()
        print("[main.py] Camera module imported, but auto-start disabled")


def main():
    """Launch the GUI and start sensor threads."""
    start_sensor_threads()

    root = tk.Tk()
    app = DarkGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

import tkinter as tk
import threading

from GUI.Joystick import OnScreenJoystick
from Controllers.MotorController import process_command as motor_run_command
from Controllers.ServoController import set_angle as set_servo_angle, outputToDashboard as servo_dashboard

# Import dashboards and sensor threads
try:
    from Controllers.GyroAccelerometerController import outputToDashboard as gyro_dashboard, run as gyro_run_loop
    from Controllers.UltrasonicController import outputToDashboard as ultra_dashboard, run as ultra_run_loop
    from Controllers.CameraController import outputToDashboard as camera_dashboard, run as camera_run
    car_status = "Connected"
except ImportError as e:
    print("[MainWindow] Hardware modules not found. This may not be running on a Raspberry Pi.")
    print("[MainWindow] Details:", e)
    gyro_run_loop = ultra_run_loop = camera_run = None
    gyro_dashboard = ultra_dashboard = motor_dashboard = camera_dashboard = {}
    car_status = "Not Connected"

# --- Runtime Flags ---
camera_running = False
gyro_running = False
ultra_running = False

def start_thread(target_func):
    if target_func:
        t = threading.Thread(target=target_func, daemon=True)
        t.start()

class DarkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Self-Driving RC Car - Dashboard")
        self.root.configure(bg="#1e1e1e")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)

        self.font_main = ("Helvetica", 12, "bold")
        self.fg_color = "#ffffff"
        self.bg_color = "#1e1e1e"
        self.button_bg = "#333333"
        self.button_active_bg = "#555555"

        self.frame_motor = self.create_labeled_frame("Motor Controls", x=20, y=20, w=380, h=300)
        self.frame_sensors = self.create_labeled_frame("Sensors", x=420, y=20, w=360, h=300)
        self.frame_camera = self.create_labeled_frame("Camera", x=800, y=20, w=380, h=300)
        self.frame_joystick = tk.Frame(self.root, bg=self.bg_color)
        self.frame_joystick.place(x=20, y=340, width=1160, height=340)

        self.build_motor_controls()
        self.build_sensor_display()
        self.build_camera_controls()
        self.build_joystick()
        self.build_servo_slider()

        self.start_threads()
        self.update_gui()

        self.root.bind("<Up>", lambda e: motor_run_command("forward"))
        self.root.bind("<Down>", lambda e: motor_run_command("backward"))
        self.root.bind("<Left>", lambda e: motor_run_command("left"))
        self.root.bind("<Right>", lambda e: motor_run_command("right"))
        self.root.bind("<space>", lambda e: motor_run_command("stop"))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_labeled_frame(self, label, x, y, w, h):
        frame = tk.LabelFrame(
            self.root, text=label,
            bg=self.bg_color, fg=self.fg_color,
            font=(self.font_main[0], 14, "bold"),
            padx=10, pady=10
        )
        frame.place(x=x, y=y, width=w, height=h)
        return frame

    def build_motor_controls(self):
        commands = ["Forward", "Backward", "Left", "Right", "Stop", "High Speed", "Medium Speed", "Low Speed"]
        actions = ["forward", "backward", "left", "right", "stop", "high", "medium", "low"]
        for label, cmd in zip(commands, actions):
            tk.Button(self.frame_motor, text=label, font=self.font_main, bg=self.button_bg, fg=self.fg_color,
                      command=lambda c=cmd: motor_run_command(c)).pack(pady=5)

    def build_sensor_display(self):
        self.sensor_text = tk.Text(self.frame_sensors, bg=self.bg_color, fg=self.fg_color, font=self.font_main, height=12)
        self.sensor_text.pack(fill="both", expand=True)

    def build_camera_controls(self):
        tk.Button(self.frame_camera, text="Start Camera", font=self.font_main, bg=self.button_bg, fg=self.fg_color,
                  command=self.start_camera).pack(pady=10)
        tk.Button(self.frame_camera, text="Stop Camera", font=self.font_main, bg=self.button_bg, fg=self.fg_color,
                  command=self.stop_camera).pack(pady=10)
        self.camera_status_label = tk.Label(self.frame_camera, text="Camera: Unknown", font=self.font_main,
                                            bg=self.bg_color, fg=self.fg_color)
        self.camera_status_label.pack(pady=10)

    def build_joystick(self):
        self.joystick_canvas = tk.Canvas(self.frame_joystick, bg="#1e1e1e", width=600, height=300, highlightthickness=0)
        self.joystick_canvas.pack(expand=True, fill="both")
        canvas_w, canvas_h = 600, 300

        self.on_screen_joystick = OnScreenJoystick(
            parent=self.joystick_canvas,
            center_x=canvas_w // 2,
            center_y=canvas_h // 2,
            base_radius=90,
            knob_radius=25,
            command_callback=self.handle_joystick
        )

        self.joystick_label = self.joystick_canvas.create_text(
            canvas_w // 2, 20, text="Joystick: STOP",
            fill="#fff", font=self.font_main
        )

    def build_servo_slider(self):
        self.servo_slider = tk.Scale(self.frame_camera, from_=0, to=180, orient="horizontal",
                                     label="Servo Angle", font=self.font_main,
                                     bg=self.bg_color, fg=self.fg_color, troughcolor="#444",
                                     highlightthickness=0, command=self.update_servo)
        self.servo_slider.pack(pady=10)

    def update_servo(self, value):
        try:
            set_servo_angle(int(value))
        except:
            pass

    def handle_joystick(self, dx, dy):
        direction = "stop"
        T = 0.3
        up, down = dy < -T, dy > T
        left, right = dx < -T, dx > T

        if up and left: direction = "forward_left"
        elif up and right: direction = "forward_right"
        elif down and left: direction = "backward_left"
        elif down and right: direction = "backward_right"
        elif up: direction = "forward"
        elif down: direction = "backward"
        elif left: direction = "left"
        elif right: direction = "right"

        self.joystick_canvas.itemconfig(self.joystick_label, text=f"Joystick: {direction.upper()}")
        motor_run_command(direction)

    def start_camera(self):
        global camera_running
        if camera_run and not camera_running:
            camera_running = True
            start_thread(camera_run)

    def stop_camera(self):
        global camera_running
        camera_running = False

    def start_threads(self):
        global gyro_running, ultra_running
        gyro_running = True if gyro_run_loop else False
        ultra_running = True if ultra_run_loop else False
        if gyro_run_loop: start_thread(gyro_run_loop)
        if ultra_run_loop: start_thread(ultra_run_loop)

    def update_gui(self):
        self.sensor_text.delete("1.0", tk.END)

        self.sensor_text.insert(tk.END, f"--- Gyro ---\n")
        for k, v in gyro_dashboard.get("gyro", {}).items():
            self.sensor_text.insert(tk.END, f"{k}: {v:.2f}\n")

        self.sensor_text.insert(tk.END, f"\n--- Accel ---\n")
        for k, v in gyro_dashboard.get("accel", {}).items():
            self.sensor_text.insert(tk.END, f"{k}: {v:.2f}\n")

        self.sensor_text.insert(tk.END, f"\n--- Ultrasonic ---\n")
        self.sensor_text.insert(tk.END, f"Distance: {ultra_dashboard.get('distance', 0):.2f} m\n")
        self.sensor_text.insert(tk.END, f"Proximity: {ultra_dashboard.get('proximity', 'N/A')}\n")

        self.sensor_text.insert(tk.END, f"\n--- Servo ---\n")
        self.sensor_text.insert(tk.END, f"Angle: {servo_dashboard.get('servo_angle', 0)}\n")

        self.sensor_text.insert(tk.END, f"\n--- Camera ---\n")
        self.sensor_text.insert(tk.END, f"Status: {camera_dashboard.get('camera_status', 'N/A')}\n")
        self.sensor_text.insert(tk.END, f"Resolution: {camera_dashboard.get('resolution', 'N/A')}\n")
        self.sensor_text.insert(tk.END, f"FPS: {camera_dashboard.get('fps', 0)}\n")
        self.sensor_text.insert(tk.END, f"Frames: {camera_dashboard.get('frame_count', 0)}\n")

        self.camera_status_label.config(text=f"Camera: {camera_dashboard.get('camera_status', 'N/A')}")
        self.root.after(200, self.update_gui)

    def on_close(self):
        global camera_running, gyro_running, ultra_running
        camera_running = gyro_running = ultra_running = False
        try:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
        except ImportError:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = DarkGUI(root)
    root.mainloop()

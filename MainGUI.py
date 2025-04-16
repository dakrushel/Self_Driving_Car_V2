# Main for GUI and gathering test scripts. Self Driving part to be added 
# later using opencv and this repo https://github.com/murtazahassan/Neural-Networks-Self-Driving-Car-Raspberry-Pi/tree/main 

import tkinter as tk
import threading
import time

# Import test scripts
try:
    from TestScripts.CameraTest import run as camera_run
    from TestScripts.CameraTest import outputToDashboard as camera_dashboard

    from Controllers.GyroAccelerometerController import outputToDashboard as gyro_dashboard, run as gyro_run_loop
    from Controllers.UltrasonicController import outputToDashboard as ultra_dashboard, run as ultra_run_loop
    from Controllers.MotorController import outputToDashboard as motor_dashboard
    car_status = "Connected"
except ImportError as e:
    print("ERROR: Some hardware modules not found. This likely means you're not on a Raspberry Pi, or smbus is missing.")
    print("Details:", e)
    # If this fails, sensor threads won't run, but we let the GUI load.
    camera_run = None
    camera_dashboard = {}
    gyro_run_loop = None
    gyro_dashboard = {}
    ultra_run_loop = None
    ultra_dashboard = {}
    motor_dashboard = {}
    car_status = "Not Connected"

# Flags for sensor/camera threads
camera_running = False
gyro_running = False
ultra_running = False

# Default motor speed
current_speed = 35

# -------------------------------
# Motor Control
# -------------------------------
def motor_run_command(cmd: str):
    """
    Direct approach referencing MotorControllerTest pins.
    On Pi, uses RPi.GPIO to set motor directions. If not on Pi or RPi.GPIO missing, does nothing.
    """
    try:
        import RPi.GPIO as GPIO
    except ImportError:
        print("RPi.GPIO not available - skipping motor command.")
        return

    in1, in2, enA = 19, 26, 13
    in3, in4, enB = 20, 21, 16

    global current_speed
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(in1, GPIO.OUT)
    GPIO.setup(in2, GPIO.OUT)
    GPIO.setup(enA, GPIO.OUT)
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)

    GPIO.setup(in3, GPIO.OUT)
    GPIO.setup(in4, GPIO.OUT)
    GPIO.setup(enB, GPIO.OUT)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)

    p = GPIO.PWM(enA, 1000)
    q = GPIO.PWM(enB, 1000)
    p.start(current_speed)
    q.start(current_speed)

    cmd = cmd.lower()

    if cmd == 'forward':
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)

    elif cmd == 'backward':
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)

    elif cmd == 'left':
        # pivot left
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)

    elif cmd == 'right':
        # pivot right
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)

    elif cmd == 'stop':
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)

    elif cmd == 'low':
        current_speed = 35
        p.ChangeDutyCycle(current_speed)
        q.ChangeDutyCycle(current_speed)

    elif cmd == 'medium':
        current_speed = 50
        p.ChangeDutyCycle(current_speed)
        q.ChangeDutyCycle(current_speed)

    elif cmd == 'high':
        current_speed = 75
        p.ChangeDutyCycle(current_speed)
        q.ChangeDutyCycle(current_speed)

    elif cmd == 'forward_left':
        # pivot style diagonal
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)

    elif cmd == 'forward_right':
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)

    elif cmd == 'backward_left':
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)

    elif cmd == 'backward_right':
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)

    # Not stopping PWM intentionally - we want continuous motor operation until next command

# -------------------------------
# Sensor Threads
# -------------------------------
def camera_thread_func():
    global camera_running
    if camera_run is None:
        print("No camera script or not on Pi.")
        return
    camera_run()
    camera_running = False

def gyro_thread_func():
    global gyro_running
    if gyro_run_loop is None:
        print("No gyro script or not on Pi.")
        return
    try:
        gyro_run_loop()
    except KeyboardInterrupt:
        pass
    gyro_running = False

def ultrasonic_thread_func():
    global ultra_running
    if ultra_run_loop is None:
        print("No ultrasonic script or not on Pi.")
        return
    try:
        ultra_run_loop()
    except KeyboardInterrupt:
        pass
    ultra_running = False

# -------------------------------
# On-Screen Joystick
# -------------------------------
class OnScreenJoystick:
    """
    A canvas-based joystick: the user drags a 'knob' inside a circular base.
    The callback is called with dx, dy in range [-1,1].
    """
    def __init__(self, parent, center_x, center_y, base_radius, knob_radius, command_callback):
        self.parent = parent
        self.cx = center_x
        self.cy = center_y
        self.base_r = base_radius
        self.knob_r = knob_radius
        self.command_callback = command_callback

        # Draw base
        self.base = parent.create_oval(
            self.cx - self.base_r, self.cy - self.base_r,
            self.cx + self.base_r, self.cy + self.base_r,
            outline="#666", width=2, fill="#333"
        )
        # Draw knob
        self.knob = parent.create_oval(
            self.cx - self.knob_r, self.cy - self.knob_r,
            self.cx + self.knob_r, self.cy + self.knob_r,
            outline="#aaa", width=1, fill="#aaa"
        )

        self.dragging = False
        # Bind events
        parent.tag_bind(self.knob, "<ButtonPress-1>", self.start_drag)
        parent.tag_bind(self.knob, "<B1-Motion>", self.drag)
        parent.tag_bind(self.knob, "<ButtonRelease-1>", self.end_drag)

    def start_drag(self, event):
        self.dragging = True

    def drag(self, event):
        if not self.dragging:
            return
        dx = event.x - self.cx
        dy = event.y - self.cy
        dist = (dx*dx + dy*dy)**0.5

        if dist > self.base_r:
            # clamp to base circle
            ratio = self.base_r / dist
            dx *= ratio
            dy *= ratio

        # move knob
        self.parent.coords(
            self.knob,
            self.cx + dx - self.knob_r, self.cy + dy - self.knob_r,
            self.cx + dx + self.knob_r, self.cy + dy + self.knob_r
        )

        # normalized -1..1
        norm_x = dx / self.base_r
        norm_y = dy / self.base_r
        self.command_callback(norm_x, norm_y)

    def end_drag(self, event):
        self.dragging = False
        # reset knob to center
        self.parent.coords(
            self.knob,
            self.cx - self.knob_r, self.cy - self.knob_r,
            self.cx + self.knob_r, self.cy + self.knob_r
        )
        self.command_callback(0, 0)


class DarkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Self-Driving RC Car - On-Screen Joystick")
        self.root.configure(bg="#1e1e1e")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)

        self.font_main = ("Helvetica", 12, "bold")
        self.fg_color = "#ffffff"
        self.bg_color = "#1e1e1e"
        self.button_bg = "#333333"
        self.button_active_bg = "#555555"

        # --- Motor Controls Frame ---
        self.frame_motor = tk.LabelFrame(
            self.root, text="Motor Controls",
            bg=self.bg_color, fg=self.fg_color,
            font=(self.font_main[0], 14, "bold"),
            padx=10, pady=10
        )
        # Widen it so speed buttons don't get cut
        self.frame_motor.place(x=20, y=20, width=380, height=300)

        # --- Sensors Frame ---
        self.frame_sensors = tk.LabelFrame(
            self.root, text="Sensors",
            bg=self.bg_color, fg=self.fg_color,
            font=(self.font_main[0], 14, "bold"),
            padx=10, pady=10
        )
        self.frame_sensors.place(x=420, y=20, width=360, height=300)

        # --- Camera Frame ---
        self.frame_camera = tk.LabelFrame(
            self.root, text="Camera",
            bg=self.bg_color, fg=self.fg_color,
            font=(self.font_main[0], 14, "bold"),
            padx=10, pady=10
        )
        self.frame_camera.place(x=800, y=20, width=380, height=300)

        # --- On-Screen Joystick Frame ---
        self.frame_joystick = tk.Frame(self.root, bg=self.bg_color)
        # place it at the bottom
        self.frame_joystick.place(x=20, y=340, width=1160, height=340)

        self.build_motor_controls()
        self.build_sensor_display()
        self.build_camera_controls()
        self.build_joystick()

        self.start_threads()
        self.update_gui()

        # Keyboard fallback
        self.root.bind("<Up>", lambda e: motor_run_command("forward"))
        self.root.bind("<Down>", lambda e: motor_run_command("backward"))
        self.root.bind("<Left>", lambda e: motor_run_command("left"))
        self.root.bind("<Right>", lambda e: motor_run_command("right"))
        self.root.bind("<space>", lambda e: motor_run_command("stop"))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_motor_controls(self):
        btn_cfg = dict(
            bg=self.button_bg, fg=self.fg_color,
            activebackground=self.button_active_bg,
            font=self.font_main, relief="flat"
        )

        tk.Button(
            self.frame_motor, text="Forward",
            command=lambda: motor_run_command("forward"),
            **btn_cfg, width=12
        ).pack(pady=5)

        tk.Button(
            self.frame_motor, text="Left",
            command=lambda: motor_run_command("left"),
            **btn_cfg, width=12
        ).pack(pady=5)

        tk.Button(
            self.frame_motor, text="Stop",
            command=lambda: motor_run_command("stop"),
            bg="#bb2d3b", fg="white", activebackground="#dd3f4c",
            font=self.font_main, relief="flat", width=12
        ).pack(pady=5)

        tk.Button(
            self.frame_motor, text="Right",
            command=lambda: motor_run_command("right"),
            **btn_cfg, width=12
        ).pack(pady=5)

        tk.Button(
            self.frame_motor, text="Backward",
            command=lambda: motor_run_command("backward"),
            **btn_cfg, width=12
        ).pack(pady=5)

        tk.Label(
            self.frame_motor,
            text="Speed Presets:",
            bg=self.bg_color, fg=self.fg_color,
            font=self.font_main
        ).pack(pady=(15, 5))

        speed_frame = tk.Frame(self.frame_motor, bg=self.bg_color)
        speed_frame.pack()

        tk.Button(
            speed_frame, text="Low",
            command=lambda: motor_run_command("low"),
            **btn_cfg, width=7
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            speed_frame, text="Med",
            command=lambda: motor_run_command("medium"),
            **btn_cfg, width=7
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            speed_frame, text="High",
            command=lambda: motor_run_command("high"),
            **btn_cfg, width=7
        ).grid(row=0, column=2, padx=5)

    def build_sensor_display(self):
        # Car Status
        self.label_carstatus = tk.Label(
            self.frame_sensors,
            text=f"Car Status: {car_status}",
            bg=self.bg_color,
            fg="#66ff66" if car_status == "Connected" else "#ff6666",
            font=self.font_main
        )
        self.label_carstatus.pack(pady=5, anchor="w")

        # Gyro
        self.label_gyro = tk.Label(
            self.frame_sensors,
            text="Gyro: N/A",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.font_main
        )
        self.label_gyro.pack(pady=10, anchor="w")

        # Ultrasonic
        self.label_ultra = tk.Label(
            self.frame_sensors,
            text="Ultrasonic: N/A",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.font_main
        )
        self.label_ultra.pack(pady=10, anchor="w")

        # Camera status
        self.label_camera = tk.Label(
            self.frame_sensors,
            text="Camera: Stopped",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.font_main
        )
        self.label_camera.pack(pady=10, anchor="w")

        # Motor
        self.label_motor = tk.Label(
            self.frame_sensors,
            text="Motor: N/A",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.font_main
        )
        self.label_motor.pack(pady=10, anchor="w")

    def build_camera_controls(self):
        btn_cfg = dict(
            bg=self.button_bg, fg=self.fg_color,
            activebackground=self.button_active_bg,
            font=self.font_main, relief="flat", width=10
        )

        tk.Button(
            self.frame_camera,
            text="Start Camera",
            command=self.start_camera,
            **btn_cfg
        ).pack(pady=10)

        tk.Button(
            self.frame_camera,
            text="Stop Camera",
            command=self.stop_camera,
            **btn_cfg
        ).pack(pady=10)

    def build_joystick(self):
        """
        Creates a canvas in self.frame_joystick with an on-screen joystick.
        The joystick calls handle_joystick(dx, dy).
        """
        self.joystick_canvas = tk.Canvas(self.frame_joystick, bg="#1e1e1e", width=600, height=300, highlightthickness=0)
        self.joystick_canvas.pack(expand=True, fill="both")

        # center it in the canvas
        # for simplicity, let's put it near center
        canvas_w = 600
        canvas_h = 300
        self.on_screen_joystick = OnScreenJoystick(
            parent=self.joystick_canvas,
            center_x=canvas_w//2,
            center_y=canvas_h//2,
            base_radius=90,
            knob_radius=25,
            command_callback=self.handle_joystick
        )

        # label for joystick status
        self.joystick_label = self.joystick_canvas.create_text(
            canvas_w//2, 20,
            text="Joystick: STOP",
            fill="#fff",
            font=("Helvetica", 12, "bold")
        )

    def handle_joystick(self, dx, dy):
        """
        Called by on-screen joystick. dx, dy in [-1..1].
        We'll map that to motor commands: forward, backward, left, right, diagonal combos, or stop.
        """
        direction = "stop"

        # We define thresholds to interpret dx, dy
        # y negative => forward, y positive => backward
        # x negative => left, x positive => right
        THRESHOLD = 0.3

        up = (dy < -THRESHOLD)
        down = (dy > THRESHOLD)
        left = (dx < -THRESHOLD)
        right = (dx > THRESHOLD)

        if up and left:
            direction = "forward_left"
        elif up and right:
            direction = "forward_right"
        elif down and left:
            direction = "backward_left"
        elif down and right:
            direction = "backward_right"
        elif up:
            direction = "forward"
        elif down:
            direction = "backward"
        elif left:
            direction = "left"
        elif right:
            direction = "right"
        else:
            direction = "stop"

        # Update label
        self.joystick_canvas.itemconfig(self.joystick_label, text=f"Joystick: {direction.upper()}")

        # Send to motor
        motor_run_command(direction)

    def start_camera(self):
        global camera_running
        if camera_run is None:
            print("Camera script not available.")
            return
        camera_running = True
        threading.Thread(target=camera_thread_func, daemon=True).start()

    def stop_camera(self):
        global camera_running
        camera_running = False

    def start_threads(self):
        global gyro_running, ultra_running

        # Start gyro
        if gyro_run_loop is not None:
            gyro_running = True
            threading.Thread(target=gyro_thread_func, daemon=True).start()
        else:
            print("No gyro script or missing smbus. Skipping gyro thread.")

        # Start ultrasonic
        if ultra_run_loop is not None:
            ultra_running = True
            threading.Thread(target=ultrasonic_thread_func, daemon=True).start()
        else:
            print("No ultrasonic script. Skipping ultrasonic thread.")

        # Optionally auto-start camera (for later)
        # camera_running = True
        # threading.Thread(target=camera_thread_func, daemon=True).start()

    def update_gui(self):
        """
        Periodically update sensor data on the GUI from the various outputToDashboard dicts.
        """
        # Gyro
        if gyro_dashboard and "gyro" in gyro_dashboard:
            gx = gyro_dashboard["gyro"]["x"]
            gy = gyro_dashboard["gyro"]["y"]
            gz = gyro_dashboard["gyro"]["z"]
            self.label_gyro.config(text=f"Gyro: x={gx:.2f}, y={gy:.2f}, z={gz:.2f}")
        else:
            self.label_gyro.config(text="Gyro: N/A")

        # Ultrasonic
        if ultra_dashboard and "distance" in ultra_dashboard:
            dist = ultra_dashboard["distance"]
            prox = ultra_dashboard["proximity"]
            self.label_ultra.config(text=f"Ultrasonic: {dist:.2f}m, {prox}")
        else:
            self.label_ultra.config(text="Ultrasonic: N/A")

        # Camera
        global camera_running
        if camera_running:
            if camera_dashboard.get("camera_status") == "Connected":
                self.label_camera.config(text="Camera: Connected")
            else:
                self.label_camera.config(text="Camera: Running...")
        else:
            self.label_camera.config(text="Camera: Stopped")

        # Motor
        if motor_dashboard:
            lf_dir = motor_dashboard["L_Front"]["direction"]
            lf_spd = motor_dashboard["L_Front"]["speed"]
            self.label_motor.config(text=f"Motor: {lf_dir} @ {lf_spd}%")
        else:
            self.label_motor.config(text="Motor: N/A")

        self.root.after(200, self.update_gui)

    def on_close(self):
        global camera_running, gyro_running, ultra_running
        camera_running = gyro_running = ultra_running = False

        # Cleanup if on Pi
        try:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
        except ImportError:
            pass

        self.root.destroy()

def main():
    root = tk.Tk()
    app = DarkGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

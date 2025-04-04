import RPi.GPIO as GPIO
import socket
import json
from time import sleep
from threading import Thread, Lock
from gpiozero import DistanceSensor

# --- Pin Configuration ---
# Right motor: forward/backward control
IN1 = 26    # Right forward
IN2 = 19    # Right backward
EN1 = 13    # Right PWM

# Left motor: forward/backward control
IN3 = 20    # Left forward
IN4 = 21    # Left backward
EN2 = 16    # Left PWM

# --- GPIO Initialization ---
GPIO.setmode(GPIO.BCM)
GPIO.setup([IN1, IN2, EN1, IN3, IN4, EN2], GPIO.OUT)
GPIO.output([IN1, IN2, IN3, IN4], GPIO.LOW)

# --- PWM Initialization ---
p = GPIO.PWM(EN1, 1000)  # Right motor PWM
q = GPIO.PWM(EN2, 1000)  # Left motor PWM
p.start(50)
q.start(50)

# --- Distance Sensor Initialization ---
# trig_pin: 23, echo_pin: 24, threshold: 0.3m
ultrasonic = DistanceSensor(echo=24, trigger=23, threshold_distance=0.3)

# --- Global Variables for Command State ---
current_command = "stop"
command_lock = Lock()
obstacle_detected = False

# --- Motor Control Functions ---
def forward():
    if check_obstacle():  # Check obstacle before moving
        print("[RCController] Obstacle detected, cannot move forward")
        stop()
        return
        
    print("[RCController] Moving forward")
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    p.ChangeDutyCycle(90)
    q.ChangeDutyCycle(90)

def backward():
    print("[RCController] Moving backward")
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    p.ChangeDutyCycle(75)
    q.ChangeDutyCycle(75)

def left():
    print("[RCController] Turning left")
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    p.ChangeDutyCycle(75)
    q.ChangeDutyCycle(75)

def right():
    print("[RCController] Turning right")
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    p.ChangeDutyCycle(75)
    q.ChangeDutyCycle(75)

def stop():
    print("[RCController] Stopping")
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    # Update the current command state to "stop"
    with command_lock:
        global current_command
        current_command = "stop"

def turn_left_forward():
    if check_obstacle():  # Check obstacle before moving
        print("[RCController] Obstacle detected, cannot move forward")
        stop()
        return
        
    print("[RCController] Turning left forward")
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    p.ChangeDutyCycle(100)
    q.ChangeDutyCycle(30)

def turn_right_forward():
    if check_obstacle():  # Check obstacle before moving
        print("[RCController] Obstacle detected, cannot move forward")
        stop()
        return
        
    print("[RCController] Turning right forward")
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    p.ChangeDutyCycle(30)
    q.ChangeDutyCycle(100)

def turn_left_backward():
    print("[RCController] Turning left backward")
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    p.ChangeDutyCycle(85)
    q.ChangeDutyCycle(30)

def turn_right_backward():
    print("[RCController] Turning right backward")
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    p.ChangeDutyCycle(30)
    q.ChangeDutyCycle(85)

def set_speed(level):
    if level == "low":
        print("[RCController] Speed set to low")
        p.ChangeDutyCycle(35)
        q.ChangeDutyCycle(35)
    elif level == "medium":
        print("[RCController] Speed set to medium")
        p.ChangeDutyCycle(50)
        q.ChangeDutyCycle(50)
    elif level == "high":
        print("[RCController] Speed set to high")
        p.ChangeDutyCycle(75)
        q.ChangeDutyCycle(75)
    else:
        print("[RCController] Unknown speed level")

# --- Helper function to check for obstacles ---
def check_obstacle():
    # Read current distance and threshold directly rather than using the triggered event
    distance = ultrasonic.distance
    print(f"[Sensor] Current distance: {distance:.2f} m")
    return distance <= ultrasonic.threshold_distance

# --- Process Command and Update Global State ---
def process_command(command):
    global current_command
    command = command.strip().lower()
    print(f"[RCController] Processing command: {command}")
    with command_lock:
        current_command = command  # Update current command

    if command == "forward":
        forward()
    elif command == "backward":
        backward()
    elif command == "left":
        left()
    elif command == "right":
        right()
    elif command == "stop":
        stop()
    elif command == "turn_left_forward":
        turn_left_forward()
    elif command == "turn_right_forward":
        turn_right_forward()
    elif command == "turn_left_backward":
        turn_left_backward()
    elif command == "turn_right_backward":
        turn_right_backward()
    elif command in ["low", "medium", "high"]:
        set_speed(command)
    else:
        print(f"[RCController] Unknown command: {command}")

# --- Sensor Monitoring Thread ---
def monitor_sensor():
    global current_command
    # Forward commands that should stop on obstacle detection
    forward_commands = {"forward", "turn_left_forward", "turn_right_forward"}
    
    while True:
        sleep(0.05)  # Check sensor more frequently (50ms)
        with command_lock:
            cmd = current_command
            
        # Only act if we're moving in a forward direction
        if cmd in forward_commands:
            if check_obstacle():
                print("[RCController] Obstacle detected during movement. Stopping!")
                stop()

# --- Socket Server Implementation ---
def start_server(host="", port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    print(f"[RCController] Listening on port {port}...")
    conn, addr = server.accept()
    print(f"[RCController] Connected by {addr}")
    
    # Start sensor monitoring thread
    sensor_thread = Thread(target=monitor_sensor, daemon=True)
    sensor_thread.start()
    
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            try:
                msg = json.loads(data.decode())
                command = msg.get("command", "")
                process_command(command)
            except Exception as e:
                print(f"[RCController] Error processing data: {e}")
    finally:
        conn.close()
        cleanup()

def cleanup():
    p.stop()
    q.stop()
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        cleanup()
import RPi.GPIO as GPIO
import time

# ---- Configuration ----
servo_pin = 18  # GPIO18 supports hardware PWM
frequency = 50  # 50Hz is standard for servo motors

# ---- Dashboard Output ----
outputToDashboard = {
    "servo_angle": 0
}

# ---- Initialization ----
initialized = False
pwm = None

def setup_servo():
    global pwm, initialized
    if initialized:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servo_pin, GPIO.OUT)
    pwm = GPIO.PWM(servo_pin, frequency)
    pwm.start(0)  # Start with pulse width 0
    initialized = True

def set_angle(angle):
    """
    Move servo to specified angle (0 to 180 degrees).
    Most servos use a duty cycle of 2.5 to 12.5 over 0–180 degrees.
    """
    setup_servo()
    if angle < 0: angle = 0
    if angle > 180: angle = 180
    duty = 2.5 + (angle / 180.0) * 10  # Convert angle to duty cycle
    pwm.ChangeDutyCycle(duty)
    outputToDashboard["servo_angle"] = angle
    time.sleep(0.3)
    pwm.ChangeDutyCycle(0)  # Prevent jitter

def cleanup():
    if pwm:
        pwm.stop()
    GPIO.cleanup()

# Optional: Command line testing
if __name__ == "__main__":
    try:
        setup_servo()
        while True:
            val = input("Enter angle (0-180) or 'e' to exit: ")
            if val.strip().lower() == 'e':
                break
            try:
                angle = int(val)
                set_angle(angle)
                print(f"Moved to: {angle}°")
            except:
                print("Invalid input.")
    finally:
        cleanup()

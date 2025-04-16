import RPi.GPIO as GPIO
import pygame

# ---- Pin Configuration (Updated) ----
in1 = 19  # Right Forward
in2 = 26
enA = 13

in3 = 20  # Left Forward
in4 = 21
enB = 16

# ---- Dashboard Output ----
outputToDashboard = {
    "L_Front": {"speed": 0, "direction": "Stopped"},
    "L_Rear":  {"speed": 0, "direction": "Stopped"},
    "R_Front": {"speed": 0, "direction": "Stopped"},
    "R_Rear":  {"speed": 0, "direction": "Stopped"},
}

# PWM controllers
p = None  # Left side
q = None  # Right side
current_speed = 35
initialized = False

def setup_gpio():
    global p, q, initialized
    if initialized:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([in1, in2, in3, in4], GPIO.OUT)
    GPIO.setup([enA, enB], GPIO.OUT)

    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)

    p = GPIO.PWM(enA, 1000)
    q = GPIO.PWM(enB, 1000)
    p.start(current_speed)
    q.start(current_speed)
    initialized = True

def set_speed(level):
    global current_speed
    level = level.lower()
    if level == "low":
        current_speed = 35
    elif level == "medium":
        current_speed = 50
    elif level == "high":
        current_speed = 75
    else:
        return
    p.ChangeDutyCycle(current_speed)
    q.ChangeDutyCycle(current_speed)
    update_speeds(current_speed)

def set_direction(direction):
    setup_gpio()
    direction = direction.lower()

    def go(fwd1, fwd2, rev1, rev2):
        GPIO.output(in1, fwd1)
        GPIO.output(in2, fwd2)
        GPIO.output(in3, rev1)
        GPIO.output(in4, rev2)

    if direction == "forward":
        go(GPIO.HIGH, GPIO.LOW, GPIO.HIGH, GPIO.LOW)
        set_motor_states("Forward", current_speed)
    elif direction == "backward":
        go(GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.HIGH)
        set_motor_states("Backward", current_speed)
    elif direction == "left":
        go(GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW)
        outputToDashboard["L_Front"]["direction"] = "Backward"
        outputToDashboard["L_Rear"]["direction"] = "Backward"
        outputToDashboard["R_Front"]["direction"] = "Forward"
        outputToDashboard["R_Rear"]["direction"] = "Forward"
        update_speeds(current_speed)
    elif direction == "right":
        go(GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH)
        outputToDashboard["L_Front"]["direction"] = "Forward"
        outputToDashboard["L_Rear"]["direction"] = "Forward"
        outputToDashboard["R_Front"]["direction"] = "Backward"
        outputToDashboard["R_Rear"]["direction"] = "Backward"
        update_speeds(current_speed)
    elif direction == "stop":
        go(GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW)
        set_motor_states("Stopped", 0)
    elif direction == "forward_left":
        go(GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW)
        outputToDashboard["L_Front"]["direction"] = "Backward"
        outputToDashboard["L_Rear"]["direction"] = "Backward"
        outputToDashboard["R_Front"]["direction"] = "Forward"
        outputToDashboard["R_Rear"]["direction"] = "Forward"
        update_speeds(current_speed)
    elif direction == "forward_right":
        go(GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH)
        outputToDashboard["L_Front"]["direction"] = "Forward"
        outputToDashboard["L_Rear"]["direction"] = "Forward"
        outputToDashboard["R_Front"]["direction"] = "Backward"
        outputToDashboard["R_Rear"]["direction"] = "Backward"
        update_speeds(current_speed)
    elif direction == "backward_left":
        go(GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.HIGH)
        outputToDashboard["L_Front"]["direction"] = "Backward"
        outputToDashboard["L_Rear"]["direction"] = "Backward"
        outputToDashboard["R_Front"]["direction"] = "Backward"
        outputToDashboard["R_Rear"]["direction"] = "Backward"
        update_speeds(current_speed)
    elif direction == "backward_right":
        go(GPIO.HIGH, GPIO.LOW, GPIO.HIGH, GPIO.LOW)
        outputToDashboard["L_Front"]["direction"] = "Forward"
        outputToDashboard["L_Rear"]["direction"] = "Forward"
        outputToDashboard["R_Front"]["direction"] = "Forward"
        outputToDashboard["R_Rear"]["direction"] = "Forward"
        update_speeds(current_speed)

def set_motor_states(direction, speed):
    outputToDashboard["L_Front"]["direction"] = direction
    outputToDashboard["L_Rear"]["direction"] = direction
    outputToDashboard["R_Front"]["direction"] = direction
    outputToDashboard["R_Rear"]["direction"] = direction
    update_speeds(speed)

def update_speeds(speed):
    outputToDashboard["L_Front"]["speed"] = speed
    outputToDashboard["L_Rear"]["speed"] = speed
    outputToDashboard["R_Front"]["speed"] = speed
    outputToDashboard["R_Rear"]["speed"] = speed

def process_command(cmd):
    setup_gpio()
    if cmd in ["low", "medium", "high"]:
        set_speed(cmd)
    else:
        set_direction(cmd)

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()
    setup_gpio()
    print("Motor Controller Ready. Type commands or 'e' to exit.")
    try:
        while True:
            cmd = input("Command: ").strip().lower()
            if cmd == 'e':
                break
            process_command(cmd)
            print(outputToDashboard)
            clock.tick(10)
    finally:
        cleanup()
        pygame.quit()

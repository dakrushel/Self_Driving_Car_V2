import RPi.GPIO as GPIO
import pygame

# ---- Pin Configuration (Updated) ----
in1 = 19  # L_Front
in2 = 26
enA = 13

in3 = 20  # R_Front
in4 = 21
enB = 16

# ---- Dashboard Output ----
outputToDashboard = {
    "L_Front": {"speed": 0, "direction": "Stopped"},
    "L_Rear":  {"speed": 0, "direction": "Stopped"},
    "R_Front": {"speed": 0, "direction": "Stopped"},
    "R_Rear":  {"speed": 0, "direction": "Stopped"},
}

def run():
    # ---- GPIO Setup ----
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

    p = GPIO.PWM(enA, 1000)  # Left side
    q = GPIO.PWM(enB, 1000)  # Right side
    p.start(35)
    q.start(35)

    # ---- Pygame Setup ----
    pygame.init()
    clock = pygame.time.Clock()

    running = True
    direction_flag = 1  # 1 = forward, 0 = backward
    current_speed = 35

    print("\nMotor Controller Ready.")
    print("Commands: r-run | s-stop | f-forward | b-backward | l-low | m-medium | h-high | tr-turn right | e-exit\n")

    while running:
        # Get keyboard input when available
        if pygame.event.peek(pygame.KEYDOWN):
            x = input().lower()

            if x == 'r':
                print("run")
                if direction_flag == 1:
                    GPIO.output(in1, GPIO.HIGH)
                    GPIO.output(in2, GPIO.LOW)
                    GPIO.output(in3, GPIO.HIGH)
                    GPIO.output(in4, GPIO.LOW)
                    set_motor_states("Forward", current_speed)
                else:
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.HIGH)
                    GPIO.output(in3, GPIO.LOW)
                    GPIO.output(in4, GPIO.HIGH)
                    set_motor_states("Backward", current_speed)

            elif x == 's':
                print("stop")
                GPIO.output(in1, GPIO.LOW)
                GPIO.output(in2, GPIO.LOW)
                GPIO.output(in3, GPIO.LOW)
                GPIO.output(in4, GPIO.LOW)
                set_motor_states("Stopped", 0)

            elif x == 'f':
                print("forward")
                direction_flag = 1
                GPIO.output(in1, GPIO.HIGH)
                GPIO.output(in2, GPIO.LOW)
                GPIO.output(in3, GPIO.HIGH)
                GPIO.output(in4, GPIO.LOW)
                set_motor_states("Forward", current_speed)

            elif x == 'b':
                print("backward")
                direction_flag = 0
                GPIO.output(in1, GPIO.LOW)
                GPIO.output(in2, GPIO.HIGH)
                GPIO.output(in3, GPIO.LOW)
                GPIO.output(in4, GPIO.HIGH)
                set_motor_states("Backward", current_speed)

            elif x == 'l':
                print("low speed")
                current_speed = 35
                p.ChangeDutyCycle(current_speed)
                q.ChangeDutyCycle(current_speed)
                update_speeds(current_speed)

            elif x == 'm':
                print("medium speed")
                current_speed = 50
                p.ChangeDutyCycle(current_speed)
                q.ChangeDutyCycle(current_speed)
                update_speeds(current_speed)

            elif x == 'h':
                print("high speed")
                current_speed = 75
                p.ChangeDutyCycle(current_speed)
                q.ChangeDutyCycle(current_speed)
                update_speeds(current_speed)

            elif x == 'tr':
                print("turning right")
                GPIO.output(in1, GPIO.LOW)
                GPIO.output(in2, GPIO.HIGH)
                GPIO.output(in3, GPIO.HIGH)
                GPIO.output(in4, GPIO.LOW)
                outputToDashboard["L_Front"]["direction"] = "Backward"
                outputToDashboard["L_Rear"]["direction"] = "Backward"
                outputToDashboard["R_Front"]["direction"] = "Forward"
                outputToDashboard["R_Rear"]["direction"] = "Forward"
                update_speeds(current_speed)

            elif x == 'e':
                print("exiting")
                running = False
                continue

            else:
                print("<<<  Invalid command  >>>")

        # Output current dashboard values
        print("--- Motor Dashboard ---")
        for motor, status in outputToDashboard.items():
            print(f"{motor}: {status['direction']} @ {status['speed']}%")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(10)

    # ---- Cleanup ----
    GPIO.cleanup()
    pygame.quit()

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

# Only run if executed directly
if __name__ == "__main__":
    run()

# Write your code here :-)
import pygame
from gpiozero import DistanceSensor

# ---- VARIABLES ----
# trigger ............. is the output/send pin on the pi
# echo ................ is the input/return pin on the pi
# threshol_distance ... the limit for in/out of range in meters

# -------- Setup ---------
pygame.init()
clock = pygame.time.Clock()

# Pin and threshold configuration
echo_pin = 24
trigger_pin = 23
threshold = 0.5

# Define sensor

# Dashboard data store
outputToDashboard = {
    "distance": 0.0,
    "proximity": "Unknown"
}

def run():
    ultrasonic = DistanceSensor(echo = echo_pin, trigger = trigger_pin, threshold_distance=threshold)
    running = True

    while running:

        outputToDashboard["distance"] = ultrasonic.distance
        outputToDashboard["proximity"] = (
            "In range" if outputToDashboard["distance"] <= ultrasonic.threshold_distance else "Out of range"
        )

        # For testing
        print(f"Distance: {outputToDashboard['distance']:.2f} m  |  Object proximity: {outputToDashboard['proximity']}")

        # Events and QUIT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Limit loop to 10 times per second
        clock.tick(10)  # 10 Hz
    
# Only run if this file is executed directly
if __name__ == "__main__":
    run()
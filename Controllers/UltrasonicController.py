import pygame
from gpiozero import DistanceSensor

# ---- Configuration ----
echo_pin = 24
trigger_pin = 23
threshold = 0.5  # meters

# ---- Dashboard Output ----
outputToDashboard = {
    "distance": 0.0,
    "proximity": "Unknown"
}

# ---- Sensor Init (singleton-style reuse) ----
ultrasonic = None

def setup_sensor():
    global ultrasonic
    if ultrasonic is None:
        ultrasonic = DistanceSensor(echo=echo_pin, trigger=trigger_pin, threshold_distance=threshold)

def read_distance():
    setup_sensor()
    distance = ultrasonic.distance
    proximity = "In range" if distance <= ultrasonic.threshold_distance else "Out of range"

    outputToDashboard["distance"] = distance
    outputToDashboard["proximity"] = proximity

    return distance, proximity

def run():
    pygame.init()
    clock = pygame.time.Clock()
    setup_sensor()

    running = True
    while running:
        read_distance()
        print(f"Distance: {outputToDashboard['distance']:.2f} m  |  Proximity: {outputToDashboard['proximity']}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    run()

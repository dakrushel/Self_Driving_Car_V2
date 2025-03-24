'''
Code adapted from:
Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
	http://www.electronicwings.com
'''
import smbus
import pygame
from time import sleep

# ---- I2C Setup ----
bus = smbus.SMBus(1)  # or smbus.SMBus(0) for older boards
Device_Address = 0x68  # MPU6050 device address

# ---- MPU6050 Registers ----
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

# ---- Dashboard Data Store ----
outputToDashboard = {
    "accel": {"x": 0.0, "y": 0.0, "z": 0.0},
    "gyro": {"x": 0.0, "y": 0.0, "z": 0.0}
}

def MPU_Init():
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    bus.write_byte_data(Device_Address, CONFIG, 0)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)
    value = ((high << 8) | low)
    if value > 32768:
        value -= 65536
    return value

def run():
    pygame.init()
    clock = pygame.time.Clock()
    MPU_Init()

    print("MPU6050 Initialized. Reading gyro and accelerometer data...")

    running = True
    while running:
        # Read raw values
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)

        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)

        # Convert to physical units
        outputToDashboard["accel"]["x"] = acc_x / 16384.0
        outputToDashboard["accel"]["y"] = acc_y / 16384.0
        outputToDashboard["accel"]["z"] = acc_z / 16384.0

        outputToDashboard["gyro"]["x"] = gyro_x / 131.0
        outputToDashboard["gyro"]["y"] = gyro_y / 131.0
        outputToDashboard["gyro"]["z"] = gyro_z / 131.0

        # Print for testing
        print(f"Gx={outputToDashboard['gyro']['x']:.2f}°/s",
              f"Gy={outputToDashboard['gyro']['y']:.2f}°/s",
              f"Gz={outputToDashboard['gyro']['z']:.2f}°/s",
              f"Ax={outputToDashboard['accel']['x']:.2f}g",
              f"Ay={outputToDashboard['accel']['y']:.2f}g",
              f"Az={outputToDashboard['accel']['z']:.2f}g")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(10)

    pygame.quit()

# Only run if executed directly
if __name__ == "__main__":
    run()

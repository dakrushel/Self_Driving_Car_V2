import smbus
import pygame
from time import sleep

# ---- I2C Setup ----
bus = smbus.SMBus(1)
Device_Address = 0x68

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

# ---- Initialization ----
def MPU_Init():
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    bus.write_byte_data(Device_Address, CONFIG, 0)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

# ---- Raw Read ----
def read_raw_data(addr):
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

# ---- Read All Axes ----
def read_sensors():
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)

    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)
    gyro_z = read_raw_data(GYRO_ZOUT_H)

    outputToDashboard["accel"]["x"] = acc_x / 16384.0
    outputToDashboard["accel"]["y"] = acc_y / 16384.0
    outputToDashboard["accel"]["z"] = acc_z / 16384.0

    outputToDashboard["gyro"]["x"] = gyro_x / 131.0
    outputToDashboard["gyro"]["y"] = gyro_y / 131.0
    outputToDashboard["gyro"]["z"] = gyro_z / 131.0

    return outputToDashboard

# ---- Loop ----
def run():
    pygame.init()
    clock = pygame.time.Clock()
    MPU_Init()
    print("[Gyro] Sensor initialized. Starting loop...")

    running = True
    while running:
        data = read_sensors()
        print(f"Gx={data['gyro']['x']:.2f} Gy={data['gyro']['y']:.2f} Gz={data['gyro']['z']:.2f} | "
              f"Ax={data['accel']['x']:.2f} Ay={data['accel']['y']:.2f} Az={data['accel']['z']:.2f}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    run()

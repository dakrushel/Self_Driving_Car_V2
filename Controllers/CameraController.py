import cv2
import time
import pygame
import numpy as np
import os

# ---- Dashboard Output ----
outputToDashboard = {
    "camera_status": "Disconnected",
    "frame_count": 0,
    "resolution": "N/A",
    "fps": 0
}

# ---- Camera State ----
camera = None
frame_count = 0
start_time = 0

# ---- Config ----
save_frames = True
save_dir = "camera_frames"
display_enabled = False  # Set to True if Pi is connected to monitor


def setup_camera():
    global camera, frame_count, start_time

    # Initialize counter
    frame_count = 0
    start_time = time.time()

    # Create directory for saved frames
    if save_frames and not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # OpenCV capture
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if camera.isOpened():
        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(camera.get(cv2.CAP_PROP_FPS))
        outputToDashboard["camera_status"] = "Connected"
        outputToDashboard["resolution"] = f"{width}x{height}"
        outputToDashboard["fps"] = fps
    else:
        outputToDashboard["camera_status"] = "Failed to connect"
        print("ERROR: Failed to initialize camera")
        return False

    return True


def capture_frame():
    global frame_count
    ret, frame = camera.read()
    if not ret:
        print("WARNING: Failed to capture frame")
        return

    frame_count += 1
    elapsed_time = time.time() - start_time
    current_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

    outputToDashboard["frame_count"] = frame_count
    outputToDashboard["fps"] = round(current_fps, 1)

    # Save frame periodically
    if save_frames and frame_count % 30 == 0:
        filename = os.path.join(save_dir, f"frame_{frame_count}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")

    # Basic image processing example
    brightness = np.mean(frame)
    if frame_count % 30 == 0:
        print(f"Brightness: {brightness:.1f}")

    if display_enabled:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Camera Feed", frame)
        cv2.imshow("Grayscale", gray_frame)


def cleanup():
    if camera:
        camera.release()
    if display_enabled:
        cv2.destroyAllWindows()
    pygame.quit()


def run():
    pygame.init()
    clock = pygame.time.Clock()

    if not setup_camera():
        return

    print("Camera ready. Press Ctrl+C to stop.")
    try:
        while True:
            capture_frame()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt

            if display_enabled and cv2.waitKey(1) & 0xFF == 27:
                break

            clock.tick(10)

    except KeyboardInterrupt:
        print("\nCamera test stopped by user.")
    finally:
        cleanup()
        print("Total frames:", frame_count)
        elapsed = time.time() - start_time
        if elapsed > 0:
            print(f"Average FPS: {frame_count / elapsed:.1f}")


if __name__ == "__main__":
    run()

"""
Camera Test Module for Raspberry Pi Self-Driving Car

Before running:
1. Pi Camera Module:
   - Connect to CSI port (blue side facing Ethernet/USB ports)
   - Enable camera in raspi-config: sudo raspi-config > Interface Options > Camera > Enable
   
2. USB Webcam:
   - Simply plug into any USB port
"""

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

def run():
    """
    Main function to initialize camera and capture frames
    """
    pygame.init()
    clock = pygame.time.Clock()
    start_time = time.time()
    
    # Create directory for saved frames if needed
    if not os.path.exists("camera_frames"):
        os.makedirs("camera_frames")
        print("Created directory: camera_frames")
    
    print("Initializing camera...")
    
    # ----- CAMERA INITIALIZATION -----

    # For Pi Camera Module (via CSI):
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    # Configure camera settings
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Check connection status
    if camera.isOpened():
        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(camera.get(cv2.CAP_PROP_FPS))
        
        outputToDashboard["camera_status"] = "Connected"
        outputToDashboard["resolution"] = f"{width}x{height}"
        outputToDashboard["fps"] = fps
        
        print(f"Camera initialized successfully")
        print(f"Resolution: {width}x{height}")
        print(f"FPS: {fps}")
    else:
        outputToDashboard["camera_status"] = "Failed to connect"
        print("ERROR: Failed to initialize camera")
        print("Troubleshooting tips:")
        print("  - Check physical connections")
        print("  - For Pi Camera: Make sure camera is enabled in raspi-config")
        print("  - For USB webcam: Try different USB port")
        return
    
    running = True
    frame_count = 0
    display_enabled = False  # Set to True if you have a display connected to Pi
    
    print("\nCamera test started. Press Ctrl+C to stop.")
    
    try:
        while running:
            # Capture frame
            ret, frame = camera.read()
            
            if ret:
                frame_count += 1
                elapsed_time = time.time() - start_time
                current_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
                
                # Update dashboard data
                outputToDashboard["frame_count"] = frame_count
                outputToDashboard["fps"] = round(current_fps, 1)
                
                # Print status (every 10 frames to reduce console output)
                if frame_count % 10 == 0:
                    print(f"Status: {outputToDashboard['camera_status']} | "
                          f"Frame: {frame_count} | "
                          f"FPS: {round(current_fps, 1)}")
                
                # Example: Convert to grayscale (basic image processing example)
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Display frames if display is enabled
                if display_enabled:
                    cv2.imshow("Camera Feed", frame)
                    cv2.imshow("Grayscale", gray_frame)
                
                # Save a frame periodically (every 30 frames)
                if frame_count % 30 == 0:
                    filename = f"camera_frames/frame_{frame_count}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"Saved {filename}")
                
                # Example: Calculate average brightness
                brightness = np.mean(frame)
                if frame_count % 30 == 0:
                    print(f"Average brightness: {brightness:.1f}")
                    
                # Example: Here you could add more image processing for your car
                # such as lane detection, obstacle detection, etc.
            else:
                print("WARNING: Failed to capture frame")
            
            # Handle pygame events for clean exit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Exit if ESC key pressed (when display is enabled)
            if display_enabled and cv2.waitKey(1) & 0xFF == 27:
                running = False
            
            # Limit framerate to not overwhelm the Pi
            clock.tick(10)
    
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    
    finally:
        # Clean up resources
        camera.release()
        if display_enabled:
            cv2.destroyAllWindows()
        pygame.quit()
        
        print("\nCamera test complete")
        print(f"Total frames captured: {frame_count}")
        print(f"Average FPS: {frame_count / (time.time() - start_time):.1f}")


# Only run if executed directly
if __name__ == "__main__":
    run()
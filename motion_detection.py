import cv2
import numpy as np
import time
from datetime import datetime

def get_vibration_intensity(ip="192.168.43.1", duration=10, log_file="vibration_log.csv"):
    """
    Capture video feed via DroidCam and compute real vibration intensity.
    """
    url = f"http://{ip}:4747/video"
    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        print("❌ Could not connect to camera. Check IP or DroidCam app.")
        return

    ret, prev_frame = cap.read()
    if not ret:
        print("⚠️ Failed to read video feed.")
        return

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    start_time = time.time()

    with open(log_file, "a") as f:
        f.write("timestamp,intensity\n")

        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(prev_gray, gray)
            vibration_intensity = np.mean(diff)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp},{vibration_intensity:.2f}\n")

            print(f"{timestamp} - Intensity: {vibration_intensity:.2f}")

            prev_gray = gray
            time.sleep(0.1)

    cap.release()
    print("✅ Data logging complete. Saved to:", log_file)
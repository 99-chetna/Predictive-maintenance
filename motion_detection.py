import cv2
import numpy as np
import time
from datetime import datetime
import os
import pandas as pd

def get_vibration_intensity(ip="192.168.43.1", duration=10, log_file="vibration_log.csv", progress_callback=None):
    """
    Continuously captures video feed from DroidCam, calculates vibration intensity,
    and logs data live to CSV file.
    """
    url = f"http://{ip}:4747/video"
    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        print("❌ Could not connect to camera. Check IP or DroidCam app.")
        return

    # Read initial frame
    ret, prev_frame = cap.read()
    if not ret:
        print("⚠️ Failed to read video feed.")
        return

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    start_time = time.time()

    # Ensure the file has a header (safe append)
    if not os.path.exists(log_file) or os.stat(log_file).st_size == 0:
        with open(log_file, "w") as f:
            f.write("timestamp,intensity\n")

    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        vibration_intensity = np.mean(diff)
        prev_gray = gray

        # Log data safely to CSV (append one line at a time)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a") as f:
            f.write(f"{timestamp},{vibration_intensity:.2f}\n")

        # If Streamlit sent a progress callback, update live chart
        if progress_callback:
            progress_callback(timestamp, vibration_intensity)

        time.sleep(0.2)

    cap.release()
    print("✅ Data logging complete.")

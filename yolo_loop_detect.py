import numpy as np
import subprocess
import sys
import cv2
from ultralytics import YOLO
import os
import time
import datetime
import signal
from gpiozero import AngularServo

# --- Configuration ---
model_path = "yolo11n_ncnn_model"
save_folder = "detections"
threshold = 0.5
capture_interval = 1

# - counter -> ensures only released if cat is in 2 consecutive pictures
count = 0

# Define our target animals (plus person)
target_classes = ["bird", "cat", "dog", "cow", "bear"]

# Set bounding box colors (BGR format for OpenCV)
bbox_colors = [
    (87, 120, 164), (228, 148, 68), (209, 97, 93), (133, 182, 178),
    (106, 159, 88), (231, 202, 96), (168, 124, 159), (241, 162, 169),
    (150, 118, 98), (184, 176, 172)
]

# --- Setup ---
os.makedirs(save_folder, exist_ok=True)

print(f"Loading NCNN model from: {model_path}")
model = YOLO(model_path)
labels = model.names

# Initialize the servo ONCE globally to avoid GPIO resource conflicts
print("Initializing servo on GPIO 14...")
my_servo = AngularServo(14, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025)
my_servo.angle = 30
time.sleep(1)
my_servo.value = None # Detach servo to save power and prevent jittering

def spray(nTimes):
    """Moves the servo back and forth nTimes."""
    for i in range(1, nTimes + 1):
        # Move to 150 degrees
        my_servo.angle = 150
        time.sleep(1)
        # Move back to 30 degrees
        my_servo.angle = 30
        time.sleep(1)
    my_servo.value = None # Detach again after spraying

print("Starting detection loop... Press Ctrl+C to stop.")

try:
    while True:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        image_path = "temp.jpg"
        box_path = f"{save_folder}/cat_{timestamp}_boxes.jpg"
        # CHANGED: We now save directly as .mp4 so the file contains proper timing headers
        video_path = f"{save_folder}/reaction_{timestamp}.mp4"

        # --- 1. Capture still image ---
        # The camera hardware is briefly claimed here
        subprocess.run([
            "rpicam-still",
            "-o", image_path,
            "--width", "640", "--height", "480",
            "--timeout", "1000",
            "--nopreview"
        ])

        # --- 2. Load temporary image ---
        try:
            frame = cv2.imread(image_path)
            if frame is None:
                print(f"Failed to load image from {image_path}")
                continue
        except Exception as e:
            print(f"Error loading image: {e}")
            continue

        # --- 3. Run detection ---
        results = model(frame, verbose=False)
        detections = results[0].boxes

        # --- 4. Process predictions ---
        detected = False
        print(f"\n[{timestamp}] Detected objects:")
        
        for i, _ in enumerate(detections):
            score = detections.conf[i].item()
            if score >= threshold:
                class_idx = int(detections.cls[i].item())
                class_name = labels[class_idx]
                print(f" - {class_name}: {score:.2f}")
                
                if class_name in target_classes:
                    detected = True

                # Get bounding box coordinates and draw them
                xyxy = detections.xyxy[i].cpu().numpy().squeeze().astype(int)
                xmin, ymin, xmax, ymax = xyxy
                color = bbox_colors[class_idx % len(bbox_colors)]
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                label = f'{class_name}: {score:.2f}'
                (label_width, label_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                label_ymin = max(ymin, label_height + 10)
                cv2.rectangle(frame, (xmin, label_ymin - label_height - 10), (xmin + label_width, label_ymin + baseline - 10), color, cv2.FILLED)
                cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # --- 5. Trigger Actions if Target Found ---
        if detected:
            count += 1  # Increment frame count here so 2 cats in 1 frame don't falsely trigger it
            print(f"Target detected! Saving annotated image to {box_path}")
            cv2.imwrite(box_path, frame)

            # -- if target was detected the second time Film and enable sprayer
            if count > 1:
                print(f"Starting video recording: {video_path}")
                # Start rpicam-vid in the background
                # We explicitly define the framerate so the .mp4 container knows how to play it
                video_process = subprocess.Popen([
                    "rpicam-vid",
                    "-t", "0",
                    "-o", video_path,
                    "--width", "1280", "--height", "720",
                    "--framerate", "30",
                    "--nopreview"
                ])
                # INCREASED WAIT TIME: Give the hardware 0.5 seconds to switch from photo to video mode
                time.sleep(0.5)

                # Trigger the water sprayer!
                print("Activating Sprayer...")
                spray(5)

                # Wait an extra second after the servo stops
                time.sleep(1)

                # Gracefully stop the background video process
                print("Stopping video recording gracefully...")
                # Send SIGINT so the .mp4 container finalizes properly
                video_process.send_signal(signal.SIGINT)
                # Wait for the file to finish saving
                video_process.wait()
                print(f"Video successfully saved and wrapped! Check: {video_path}")

                # reset count
                count = 0
        else:
            # if no detections occured - reset counter to 0
            count = 0 

        # Wait before taking the next picture
        time.sleep(capture_interval)

except KeyboardInterrupt:
    print("\nDetection loop stopped by user.")

finally:
    # Ensure the servo is safely detached on exit
    my_servo.value = None

import cv2
import numpy as np
import os
import pygame
import time
from keras.models import load_model

os.environ['TF_USE_LEGACY_KERAS'] = '1'

# Global Variables
running = False
slouch_detected_global = False

# Load Model & Labels
model = load_model("keras_model.h5", compile=False)
class_names = [line.strip() for line in open("labels.txt", "r").readlines()]

def run_posture_detection():
    global running, slouch_detected_global
    running = True
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    calibration_start = time.time()

    while running:
        success, frame = cap.read()
        if not success or not running:
            break
        frame = cv2.flip(frame, 1)

        # 1. Image Pre-processing
        display_frame = frame.copy()
        image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
        image = (image / 127.5) - 1

        # 2. Prediction
        prediction = model.predict(image, verbose=0)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        # 3. Update Global Status
        if "Slouching" in class_name and confidence_score > 0.8:
            slouch_detected_global = True
            color = (0, 0, 255) # Red
            status_text = "Slouching"
        else:
            slouch_detected_global = False
            color = (0, 255, 0) # Green
            status_text = "Good Posture"

        # 4. Visual Feedback in OpenCV Window
        if time.time() - calibration_start < 5:
            cv2.putText(display_frame, "CALIBRATING...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        cv2.putText(display_frame, f"{status_text}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        cv2.imshow("ZenFlow AI Monitor", display_frame)

        # Allow stopping via 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False # Set running to false to trigger cleanup
            break
    
    cap.release()
    cv2.destroyAllWindows()

def stop_detection():
    global running
    running = False
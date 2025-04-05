## Sean Lai
### Example Workflow before plugin segmentation.
### SNIPPET FOR LOCAL EXPERIMENTAL CORELINK VERSION
import sys 
from dotenv import load_dotenv
import os
load_dotenv()
sys.path.append(os.getenv("CL_EXP_PATH"))
#### DONT INCLUDE THE ABOVE IF USING PyPI V
# import corelink
# from corelink import processing

#import ml packages
import cv2
import numpy as np
from ultralytics import YOLO


def main():
    cap = cv2.VideoCapture(0)
    model = YOLO("yolov8n.pt")
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Process the frame using YOLOv8
        results = model.predict(frame, conf=0.5, show=True)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break

main()

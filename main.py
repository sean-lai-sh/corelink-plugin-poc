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


def findHuman(results):
    for result in results:
        boxes = result.boxes.cpu().numpy()
        
        # Get all detected objects in this frame
        class_ids = boxes.cls
        confidences = boxes.conf
        xyxys = boxes.xyxy
        
        # Check if any detection is a person
        for i, class_id in enumerate(class_ids):
            class_name = result.names[int(class_id)]
            if class_name == "person":
                print(f"Found human with confidence {confidences[i]:.2f} at {xyxys[i]}")
                return (True, xyxys[i])
    
    return (False, None)

def main():
    cap = cv2.VideoCapture(0)
    model = YOLO("yolov8n.pt")
    model.fuse()
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Process the frame using YOLOv8
        results = model(frame, conf=0.5)
        
        findHuman(results)
        ## Pause until I press 'a' to continue
        key = cv2.waitKey(1) & 0xFF
    
        if key == ord('a'):
            print("Continuing to next frame")
            continue
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break
main()

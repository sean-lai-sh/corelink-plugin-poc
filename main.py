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

# Import ML packages
import cv2
import numpy as np
from ultralytics import YOLO
# import mediapipe as mp

# mp_hands_draw = mp.solutions.drawing_utils
# mp_hands = mp.solutions.hands

def findHuman(results):
    biggest_area = 0
    best_box = None

    for result in results:
        boxes = result.boxes.cpu().numpy()

        class_ids = boxes.cls
        confidences = boxes.conf
        xyxys = boxes.xyxy

        for i, class_id in enumerate(class_ids):
            class_name = result.names[int(class_id)]
            if class_name == "person":
                x_min, y_min, x_max, y_max = xyxys[i]
                area = max(0, x_max - x_min) * max(0, y_max - y_min)
                print(f"Found human with confidence {confidences[i]:.2f} at {xyxys[i]}, area: {area}")

                if area > biggest_area:
                    biggest_area = area
                    best_box = xyxys[i]

    if best_box is not None:
        return True, best_box
    else:
        return False, None

# def detect_hands_in_human_box(frame, box_xyxy, hands):
#     x_min, y_min, x_max, y_max = map(int, box_xyxy)

#     # Crop the region of interest
#     cropped = frame[y_min:y_max, x_min:x_max]

#     # Convert to RGB for MediaPipe
#     rgb_cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)

#     # Detect hands in cropped region
#     results = hands.process(rgb_cropped)

#     if results.multi_hand_landmarks:
#         for hand_landmarks in results.multi_hand_landmarks:
#             mp_hands_draw.draw_landmarks(cropped, hand_landmarks, mp_hands.HAND_CONNECTIONS)

#             for landmark in hand_landmarks.landmark:
#                 abs_x = int(x_min + landmark.x * (x_max - x_min))
#                 abs_y = int(y_min + landmark.y * (y_max - y_min))
#                 cv2.circle(frame, (abs_x, abs_y), 3, (0, 255, 0), -1)  # Draw on full frame

    return frame

def main():
    cap = cv2.VideoCapture(0)
    model = YOLO("yolov8n.pt")
    model.fuse()

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # with mp_hands.Hands(
    #     static_image_mode=False,
    #     max_num_hands=2,
    #     min_detection_confidence=0.5,
    #     min_tracking_confidence=0.5
    # ) as hands:

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        results = model(frame, conf=0.5)
        found, human_box = findHuman(results)

        # if found:
        #     frame = detect_hands_in_human_box(frame, human_box, hands)

        # cv2.imshow("YOLO + MediaPipe Hands", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('a'):
            print("Continuing to next frame")
            continue
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

main()

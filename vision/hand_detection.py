import cv2
from .gestures import detect_hand_gesture
import mediapipe as mp

mp_hands_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def detect_hands_in_box(frame, box_xyxy, hands):
    x_min, y_min, x_max, y_max = map(int, box_xyxy)
    cropped = frame[y_min:y_max, x_min:x_max]
    rgb_cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_cropped)

    gesture = None
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_hands_draw.draw_landmarks(cropped, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = detect_hand_gesture(hand_landmarks.landmark)
            for landmark in hand_landmarks.landmark:
                abs_x = int(x_min + landmark.x * (x_max - x_min))
                abs_y = int(y_min + landmark.y * (y_max - y_min))
                cv2.circle(frame, (abs_x, abs_y), 3, (0, 255, 0), -1)

    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
    return frame, gesture

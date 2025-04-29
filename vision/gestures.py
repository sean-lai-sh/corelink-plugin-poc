from utils.math_utils import euclidean
'''
Deprecated over Smart Mediapipe Transformer Version
'''
def is_finger_extended(landmarks, tip_id, base_id, wrist_id=0):
    wrist = landmarks[wrist_id]
    base = landmarks[base_id]
    tip = landmarks[tip_id]
    return euclidean(tip, wrist) > euclidean(base, wrist)

def detect_hand_gesture(landmarks):
    fingers = [(4, 2), (8, 5), (12, 9), (16, 13), (20, 17)]
    extended_count = sum(is_finger_extended(landmarks, tip, base) for tip, base in fingers)
    return "Palm" if extended_count >= 4 else "Fist"

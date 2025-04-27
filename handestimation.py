from dotenv import load_dotenv
import os
import sys
load_dotenv()
sys.path.append(os.getenv("CL_PATH"))
import corelink # type: ignore

from asyncio import sleep
from transformers import pipeline
from PIL import Image
from .vision.human_detection import find_human
import cv2
from ultralytics import YOLO
pipe = pipeline("image-classification", model="dima806/hand_gestures_image_detection", use_fast=True)

senderID = None
receiverID = None

cap = cv2.VideoCapture(0)
model = YOLO("yolov8n.pt")
model.fuse()

def inference(image):
    """
    Perform inference on the given image using the hand gesture classification model.

    Args:
        image (numpy.ndarray): The input image in BGR format.

    Returns:
        str: The predicted hand gesture label.
    """
    results = model(image, conf=0.5)
    found, human_box = find_human(results)
    if not found:
        return "call"
    cv2_image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(cv2_image_rgb)
    # Perform inference
    results = pipe(pil_image)
    # Extract the label from the results
    label = results[0]['label']
    print(label)
    # Send the label to the Corelink serve
    corelink.send_data(senderID, label.encode("utf-8"), metadata="hand_gesture")
    return label


    

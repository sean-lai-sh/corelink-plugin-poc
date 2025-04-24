from dotenv import load_dotenv
import os
import sys
load_dotenv()
sys.path.append(os.getenv("CL_PATH"))
import corelink # type: ignore

from asyncio import sleep
from transformers import pipeline
from PIL import Image
import cv2
pipe = pipeline("image-classification", model="dima806/hand_gestures_image_detection", use_fast=True)

senderID = None
receiverID = None

def inference(image):
    """
    Perform inference on the given image using the hand gesture classification model.

    Args:
        image (numpy.ndarray): The input image in BGR format.

    Returns:
        str: The predicted hand gesture label.
    """
    cv2_image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(cv2_image_rgb)
    # Perform inference
    results = pipe(pil_image)
    # Extract the label from the results
    label = results[0]['label']
    print(label)
    # Send the label to the Corelink server
    list = corelink.list_streams(workspaces=["Holodeck"])
    corelink.send_data(senderID, label.encode("utf-8"), metadata="hand_gesture")
    return label

async def main():
    await corelink.connect("Testuser", "Testpassword", "127.0.0.1", "20012")
    await corelink.set_data_callback(inference)
    StreamID = None
    meta = "cv2imgin"
    senderID = await corelink.create_sender("Holodeck", "tcp", "testing", metadata="hand_gesture")
    while StreamID is None:
        streamList = await corelink.list_streams(workspaces=["Holodeck"])
        for stream in streamList:
            if stream["metadata"] == meta:
                StreamID = await corelink.create_receiver("Holodeck", "tcp", metadata="inference",stream_id=stream["streamID"])
                print("subscribed to a steam")
                break

    
    # While true:

    

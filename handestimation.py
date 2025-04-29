from dotenv import load_dotenv
import os
import sys
load_dotenv()
sys.path.append(os.getenv("CL_PATH"))
import corelink # type: ignore

from asyncio import sleep
from transformers import pipeline
from PIL import Image
from vision.human_detection import find_human
import cv2
from ultralytics import YOLO
pipe = pipeline("image-classification", model="dima806/hand_gestures_image_detection", use_fast=True)

senderID = None
receiverID = None

cap = cv2.VideoCapture(0)
model = YOLO("yolov8n.pt")
model.fuse()

metadata = 'cv2imgin'

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
    corelink.send(senderID, label.encode("utf-8"), type="hand_gesture")
    return label

async def byte_to_string(message , streamID, header):
    streamInfo = await corelink.stream_info(streamID)
    
    if streamInfo["meta"] == metadata:
        arr = np.frombuffer(data_bytes, dtype=np.uint8)
        label = inference(arr)
        await corelink.send(senderID, label)
        print("Label", label)
        print(streamInfo)
    
async def updateCallback(response, key):
    if response["meta"] == metadata:
        await corelink.subscribe_to_stream(receiverID, response["streamID"])
        print("updateCallback: ", response["streamID"])

async def main():
    # Init the corelink connection via control stream and user pw
    # 20012 is the default port for the control stream (this is a ws connection)
    await corelink.connect("Testuser", "Testpassword", "127.0.0.1", "20012") #TODO: For prod env switch to .env vars since we cannot assume config of external corelink server
    await corelink.set_data_callback(byte_to_string) #
    await corelink.set_server_callback(updateCallback, key="update")
    # print(await corelink.list_streams(workspaces=["Holodeck"]))
    global senderID
    senderID = await corelink.create_sender("Holodeck", "tcp", "testing", metadata="hand_gesture", data_type="string")
    global receiverID 
    receiverID = await corelink.create_receiver("Holodeck", "tcp", metadata=metadata, alert=True, echo=True, subscribe=False, data_type="image")

    while True:
        await corelink.asyncio.sleep(10000)  # Sleep for 10 seconds to keep coroutine alive

corelink.run(main())

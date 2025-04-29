from dotenv import load_dotenv
import os
import sys
load_dotenv()
sys.path.append(os.getenv("CL_PATH"))
import corelink # type: ignore

# Helper Packages
import numpy as np
import cv2
import json

# ML package import and Setup
from transformers import pipeline
from PIL import Image
from vision.human_detection import find_human
import cv2
from ultralytics import YOLO
pipe = pipeline("image-classification", model="dima806/hand_gestures_image_detection", use_fast=True)

senderID = None
receiverID = None
data_type = 'cv2imgin'

current_buffer = bytearray()
current_counter = 0
current_bytes = 0

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
    #Check human is in frame
    label = ""
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = model(image, conf=0.5)
    found, human_box = find_human(results)
    
    if not found:
        label = "no_human"
    # Identify Gesture
    pil_image = Image.fromarray(image)
    results = pipe(pil_image)
    # Extract the label from the results
    if len(results) == 0:
        label = "no_gesture"
    else:
        label = results[0]['label']
    print("Recognized Hand label:", label)
    # Send the label to the Corelink serve
    corelink.send(senderID, label)
    return label

VERBOSE = os.getenv("VERBOSE", "False") == "True" or "--verbose" in sys.argv
async def vprint(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


async def process_chunk(data_bytes, streamID, header):
    global current_buffer, current_counter, current_bytes
    
    # Step 1: Parse the JSON header
    head_info = json.loads(header)
    seq_num = head_info["seq-num"]
    seq_num_end = head_info["seq-num-end"]
    last_chunk = head_info["last-chunk"]
    file_size = head_info["file-size"]
    index = head_info["index"]

    # Step 2: Initialize buffer if starting new image
    if current_counter == 0:
        current_buffer = bytearray(file_size)

    # Step 3: Insert received data into the correct location
    current_buffer[seq_num:seq_num_end] = data_bytes
    current_counter += len(data_bytes)

    # Step 4: If we have received the full image
    if last_chunk:
        # Decode from buffer into a real image
        await vprint(f"Trying to decode image: buffer size = {len(current_buffer)} bytes")

        img = np.frombuffer(current_buffer, dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        inference(img)
        # Reset for the next image
        current_buffer = bytearray()
        current_counter = 0
        current_bytes = 0

        await vprint(f"Received complete image of size: {file_size} bytes (index {index})")
        
        # OPTIONAL: Process or display
        cv2.imshow("Received Image", img)
        cv2.waitKey(1)

async def data_callback(message , streamID, header):
    '''
    Callback function to process incoming data from the stream.
    Only runs if the stream type matches the expected data type.
    Args:
        message (bytes): The incoming data message.
        streamID (str): The ID of the stream.
        header (str): The header information for the data.
    '''
    streamInfo = await corelink.stream_info(streamID)
    if streamInfo["type"] == data_type:
        await process_chunk(message, streamID, header)
        await vprint("Index of Data", header)
    else:
        await vprint(streamInfo)
    
# THIS WORKS FOR ASYNC CALLBACKS
async def updateCallback(response, key):
    if response["type"] == data_type:
        await corelink.subscribe_to_stream(receiverID, response["streamID"])
        print("updateCallback: ", response["streamID"])
    
    
async def main():
    # Init the corelink connection via control stream and user pw
    # 20012 is the default port for the control stream (this is a ws connection)
    await corelink.connect("Testuser", "Testpassword", "127.0.0.1", "20012") #TODO: For prod env switch to .env vars since we cannot assume config of external corelink server
    await corelink.set_data_callback(data_callback) #
    await corelink.set_server_callback(updateCallback, key="update")
    await vprint(await corelink.list_streams(workspaces=["Holodeck"]))
    global senderID
    senderID = await corelink.create_sender("Holodeck", "tcp", "testing", data_type="hand_gesture")
    global receiverID 
    receiverID = await corelink.create_receiver("Holodeck", "tcp", data_type=data_type, metadata="cv2imgin", alert=True, echo=True, subscribe=False)

    lst = await corelink.list_streams(workspaces=["Holodeck"])
    for stream in lst:
        if stream["type"] == data_type:
            await corelink.subscribe_to_stream(receiverID, stream["streamID"])
            print("Connecting to existing stream at ID: ", stream["streamID"])

    while True:
        await corelink.asyncio.sleep(10000)  # Sleep for 10 seconds to keep coroutine alive
        if cv2.waitKey(1) & 0xFF == 27:
            corelink.disconnect_senders([senderID])
        
corelink.run(main())

# Load from custom experimental version of Corelink
from dotenv import load_dotenv
import os
import sys
load_dotenv()
sys.path.append(os.getenv("CL_PATH"))

## Corelink libs
import corelink
from corelink import processing

import numpy as np
import cv2
import json

# ## Checking for logging
# isLogging = os.getenv("ENABLE_LOGS")
# import logging
# if isLogging == "True":
#     # Configure logging
#     logging.basicConfig(
#         filename='log.txt',
#         filemode='a',  # append mode
#         format='%(asctime)s [%(levelname)s] %(message)s',
#         level=logging.INFO
#     )

VERBOSE = os.getenv("VERBOSE", "False") == "True" or "--verbose" in sys.argv
async def vprint(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

senderID = None
receiverID = None
data_type = 'cv2imgin'

current_buffer = bytearray()
current_counter = 0
current_bytes = 0
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
        print(f"Trying to decode image: buffer size = {len(current_buffer)} bytes")

        img = np.frombuffer(current_buffer, dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)

        # Reset for the next image
        current_buffer = bytearray()
        current_counter = 0
        current_bytes = 0

        print(f"Received complete image of size: {file_size} bytes (index {index})")
        
        # OPTIONAL: Process or display
        cv2.imshow("Received Image", img)
        cv2.waitKey(1)

    


async def byte_to_string(message , streamID, header):
    streamInfo = await corelink.stream_info(streamID)
    if streamInfo["type"] == data_type:
        await process_chunk(message, streamID, header)
        #await corelink.send(senderID, decoded_message)
        # vprint("Decoded message: ", decoded_message)
        print("Index of Data", header)
        #print(streamInfo)
    else:
        vprint(streamInfo)
    
# THIS WORKS FOR ASYNC CALLBACKS
async def updateCallback(response, key):
    if response["type"] == data_type:
        await corelink.subscribe_to_stream(receiverID, response["streamID"])
        print("updateCallback: ", response["streamID"])
    
    
async def main():
    # Init the corelink connection via control stream and user pw
    # 20012 is the default port for the control stream (this is a ws connection)
    await corelink.connect("Testuser", "Testpassword", "127.0.0.1", "20012") #TODO: For prod env switch to .env vars since we cannot assume config of external corelink server
    await corelink.set_data_callback(byte_to_string) #
    await corelink.set_server_callback(updateCallback, key="update")
    print(await corelink.list_streams(workspaces=["Holodeck"]))
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

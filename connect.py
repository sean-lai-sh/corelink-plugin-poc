# Load from custom experimental version of Corelink
from dotenv import load_dotenv
import os
import sys
load_dotenv()
sys.path.append(os.getenv("CL_PATH"))

## Corelink libs
import corelink
from corelink import processing

## Checking for logging
isLogging = os.getenv("ENABLE_LOGS")
import logging
if isLogging == "True":
    # Configure logging
    logging.basicConfig(
        filename='log.txt',
        filemode='a',  # append mode
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.INFO
    )


senderID = None
receiverID = None

async def byte_to_string(data_bytes , streamID, header):
    # print(data_bytes)
    string_data = data_bytes.decode('utf-8')
    print("RECIEVING WORD ", string_data)
    logging.info(string_data)
    # print(await corelink.list_streams(workspaces=["Holodeck"]))
    await corelink.send(senderID, string_data) 

async def changeReceiver(response, key):
    lst = await corelink.list_streams(workspaces="Holodeck")
    print(lst)
    print("response ", response)
    print("key ", key)

async def main():
    await corelink.connect("Testuser", "Testpassword", "127.0.0.1", "20012")
    await corelink.set_data_callback(byte_to_string)
    await corelink.set_server_callback(changeReceiver, key="update")
    print(await corelink.list_streams(workspaces=["Holodeck"]))
    global senderID
    senderID = await corelink.create_sender("Holodeck", "tcp", "testing", metadata="hand_gesture", data_type="string")
    global receiverID
    while receiverID is None:
        stream_lists = await corelink.list_streams(workspaces=["Holodeck"])
        for stream in stream_lists:
            if stream["meta"] == "cv2imgin":
                receiverID = await corelink.create_receiver("Holodeck", "tcp", metadata=stream['meta'], alert=True, echo=True, subscribe=False)
                await corelink.subscribe_to_stream(receiverID, stream["streamID"])
                print("Successfully created reciever with ID: ", receiverID)
                break
        await corelink.asyncio.sleep(10)

    while True:
        await corelink.asyncio.sleep(10000)  # Sleep for 10 seconds
        
corelink.run(main())

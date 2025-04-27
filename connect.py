# Load from custom experimental version of Corelink
from dotenv import load_dotenv
import os
import sys
load_dotenv()
sys.path.append(os.getenv("CL_PATH"))

## Corelink libs
import corelink
from corelink import processing

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


senderID = None
receiverID = None
metadata = 'cv2imgin'

async def byte_to_string(message , streamID, header):
    streamInfo = await corelink.stream_info(streamID)
    
    if streamInfo["meta"] == metadata:
        decoded_message = message.decode('utf-8')
        await corelink.send(senderID, decoded_message)
        print("Decoded message: ", decoded_message)
        print(streamInfo)
    else:
        print(streamInfo)
    # print("streamID ",streamID, " Data bytes ", message, " header ",header,"\n")
    # lst = await corelink.list_streams(workspaces=["Holodeck"])
    # for stream in lst:
    #     if stream["meta"] == metadata:
    #         print("streamID ", stream["streamID"], " meta ", stream["meta"])
    #         # Decode the byte data to a string
    #         decoded_message = message.decode('utf-8')
    #         print("Decoded message: ", decoded_message)
    #         # Send the decoded message to the sender
    #         await corelink.send(senderID, decoded_message)
    #         break
    
# THIS WORKS FOR ASYNC CALLBACKS
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
    receiverID = await corelink.create_receiver("Holodeck", "tcp", metadata=metadata, alert=True, echo=True, subscribe=False, data_type="string")

    while True:
        await corelink.asyncio.sleep(10000)  # Sleep for 10 seconds to keep coroutine alive
        
corelink.run(main())

from asyncio import sleep
from transformers import pipeline
from PIL import Image
import cv2
import corelink
pipe = pipeline("image-classification", model="dima806/hand_gestures_image_detection", use_fast=True)


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
    return label


async def call_back(databytes, streamID):
    s_ids = await corelink.list_streams("Holodeck")
    # find id that matches our metadata
    for id in s_ids:
        if id["metadata"] == "handest1mation":
            streamID = id["streamID"]
            break


async def main():
    await corelink.connect("Testuser", "Testpassword", "127.0.0.1", "20012")
    await corelink.set_data_callback(inference)
    await corelink.set_server_callback(call_back, key="update")
    StreamID = await corelink.create_receiver("Holodeck", "tcp", alert=True, echo=True)
    senderID = await corelink.create_sender("Holodeck", "tcp", "testing", metadata="handest1mation")
    await corelink.processing.connect_receiver(StreamID)
    # While true:

        


class connectionInfo:
    def __init__(self, user, password, ip, port):
        self.user = user
        self.password = password
        self.ip = ip
        self.port = port

class cl_plugin:
    def __init__(self, workspaceInfo: connectionInfo, recieverInfo, senderInfo, data_callback = None):
        self.workspaceInfo = workspaceInfo
        self.recieverInfo = recieverInfo
        self.senderInfo = senderInfo
        self.callback = data_callback
        self.sender_streamID = None
        self.receive_streamID = None

    @property
    def callback(self): #TODO: impl this to on update of server identify which stream matches via metadata of receiver. then connect to that stream
        return "this works :)"
    
    
    def set_callback(self, callback):
        self.callback = callback

    async def launch(self):
        ## Step 0; Init corelink workspace :)
        await corelink.connect(self.workspaceInfo.user, self.workspaceInfo.password, self.workspaceInfo.ip, self.workspaceInfo.port)
        ## step1; Init corelink sender
        self.sender_streamID = await corelink.create_sender(self.senderInfo.workspace, self.senderInfo.protocol, self.senderInfo.name, metadata=self.senderInfo.metadata)
        ## setup to ensure our server callback is running (our own internal function)
        await corelink.set_server_callback(self.callback, key="update")
        ## step 2; Init corelink receiver
        

    async def run(self):
        # Run during the loop 
        # run our send function
        self.launch()




    

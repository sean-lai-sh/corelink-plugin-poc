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
    if(print())



async def main():
    await corelink.connect("Testuser", "Testpassword", "127.0.0.1", "20012")
    await corelink.set_data_callback(inference)
    StreamID = await corelink.create_receiver("Holodeck", "tcp", alert=True, echo=True)
    senderID = await corelink.create_sender("Holodeck", "tcp", "testing")
    await corelink.processing.connect_receiver(StreamID)
    # While true:

        


class connectionInfo:
    def __init__(self, user, password, ip, port):
        self.user = user
        self.password = password
        self.ip = ip
        self.port = port

class cl_plugin:
    def __init__(self, connect, recieve_info, meta="default plugin"):
        self.connection = connect
        self.meta = meta
        self.callback = None
        self.recieve_streamID = None
        self.pipe = pipeline("image-classification", model="dima806/hand_gestures_image_detection", use_fast=True)
    
    async def run_plugin(self, callback):
        self.callback = callback
        while True:
            data = self.recieve()
            if data:
                # Process the received data
                print(f"Received data: {data}")
                # Call the callback function with the received data
                self.callback(data)
            else:
                break

    async def get_reciever(self, callback):
        if self.callback is None:
            self.callback = callback
        await corelink.set_data_callback(self.callback)
        


    

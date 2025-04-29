import time
import numpy as np
from dotenv import load_dotenv
import os
import sys
load_dotenv()
sys.path.append(os.getenv("CL_PATH"))
import corelink
import cv2
import json
import asyncio
import numpy as np


img_count = 0
start_loop = False
senderID = None

chunk_size = 1024  # 1 KB

# def compress_frame(frame, quality=30):
#     encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
#     success, encoded_img = cv2.imencode('.jpg', frame, encode_param)
#     if not success:
#         raise ValueError("Failed to compress frame")
#     return encoded_img.tobytes()

def compress_frame(frame, target_size_bytes=4*1024, quality=50, scale=1.0):
    """Compress frame, scaling and adjusting to target size."""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

    # First resize if necessary
    if scale < 1.0:
        frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    # Try compressing
    success, encoded_img = cv2.imencode('.jpg', frame, encode_param)
    if not success:
        raise ValueError("Failed to compress frame")

    output = encoded_img.tobytes()

    # If still too big, resize and compress again
    while len(output) > target_size_bytes and scale > 0.1:
        scale *= 0.8  # shrink more
        frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        success, encoded_img = cv2.imencode('.jpg', frame, encode_param)
        if not success:
            raise ValueError("Failed to compress frame")
        output = encoded_img.tobytes()

    return output

async def send_chunk(frame_bytes: bytes):
    global start_loop
    buffer_length = len(frame_bytes)
    counter = 0
    index = 0

    print(f"Buffer length: {buffer_length}")

    while counter < buffer_length:
        start_loop = False

        end = min(counter + chunk_size, buffer_length)
        chunk = frame_bytes[counter:end]
        last_chunk = (end == buffer_length)
        metadata_str = json.dumps({
            "seq-num": counter,
            "seq-num-end": end,
            "last-chunk": last_chunk,
            "file-size": buffer_length,
            "index": index
        })
        await corelink.send(senderID, chunk, user_header=metadata_str, encode=False)

        print(f"Sent chunk {index} from {counter} to {end} (last_chunk={last_chunk})")

        counter += chunk_size
        index += 1

        await asyncio.sleep(0.15)  # 150 ms between chunks

    start_loop = True

async def main():
    global senderID
    await corelink.connect("Testuser", "Testpassword", "127.0.0.1", "20012")
    # Open a websocket socket connection to the server (20012 refers to Secure WS Control Channel)
    senderID = await corelink.create_sender("Holodeck", "tcp", "testing", data_type="cv2imgin") # Holodeck is the name of the stream and udp is the type of stream
    
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert the buffer to bytes
        compressed_data = compress_frame(frame)
        await send_chunk(compressed_data)

        # Display the frame (optional)
        cv2.imshow('Frame', frame)
        await corelink.asyncio.sleep(1/30)
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # if control C is pressed, break the loop
        if cv2.waitKey(1) & 0xFF == 27:
            corelink.disconnect_senders([senderID])
    cap.release()
    cv2.destroyAllWindows()
    
        
        


corelink.run(main())

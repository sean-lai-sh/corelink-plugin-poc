import cv2
from dotenv import load_dotenv
import os
import sys
load_dotenv()
sys.path.append(os.getenv("CL_PATH"))
import corelink
import asyncio
import struct
import time
import math

# Constants
CHUNK_SIZE = 32 * 1024  # 32 KB
HEADER_SIZE = 14  # Timestamp (8 bytes) + frame number (2 bytes) + chunk index (2 bytes) + total chunks (2 bytes)
VALIDATION_TIMEOUT = 15  # seconds
RETRY_COUNT = 5
RETRY_DELAY = 0.01  # seconds

# Globals
validConnection = False
frame_counter = 0
sender_id = None

# Corelink Callbacks
async def callback(data_bytes, streamID, header):
    print(f"Received data from stream {streamID} (ignored): {len(data_bytes)} bytes")

async def subscriber(response, key):
    global validConnection
    print(f"subscriber: {response}")
    validConnection = True

async def dropped(response, key):
    global validConnection
    print(f"dropped: {response}")
    validConnection = False

async def update(response, key):
    print(f'update: {response}')

async def stale(response, key):
    print(f"stale: {response}")

async def check_connection():
    global validConnection
    while True:
        await asyncio.sleep(VALIDATION_TIMEOUT)
        if not validConnection:
            print("Connection not validated, retrying...")

# Function to send a chunk of a file
async def send_file_chunk(chunk, frame_counter, chunk_index, total_chunks, timestamp):
    buffer = bytearray(HEADER_SIZE + len(chunk))
    struct.pack_into('>QHHH', buffer, 0, timestamp, frame_counter, chunk_index, total_chunks)
    buffer[HEADER_SIZE:] = chunk

    retries = 0
    while retries < RETRY_COUNT:
        try:
            await corelink.send(sender_id, buffer)
            return
        except PermissionError as e:
            retries += 1
            print(f"Failed to send chunk {chunk_index}/{total_chunks} for frame {frame_counter}: {e}. Retrying {retries}/{RETRY_COUNT}...")
            await asyncio.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"Failed to send chunk {chunk_index}/{total_chunks} for frame {frame_counter} due to error: {e}")
            break

# Function to send an entire file by splitting it into chunks
async def send_file(file_data, frame_counter):
    file_size = len(file_data)
    total_chunks = math.ceil(file_size / CHUNK_SIZE)
    timestamp = int(time.time() * 1000)  # Convert to milliseconds

    tasks = [
        send_file_chunk(file_data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE], frame_counter, i, total_chunks, timestamp)
        for i in range(total_chunks)
    ]
    await asyncio.gather(*tasks)

async def send_end_message():
    end_message = b'FINISHED'
    try:
        await corelink.send(sender_id, end_message)
        print('End message sent.')
    except Exception as e:
        print(f"Failed to send end message: {e}")

async def main():
    global validConnection, sender_id, frame_counter

    # Connect to Corelink
    print("Connecting to Corelink server...")
    await corelink.connect("Testuser", "Testpassword", "127.0.0.1", "20012")
    
    # Create sender
    print("Creating sender...")
    sender_id = await corelink.create_sender("Holodeck", "tcp", "testing", metadata="cv2imgin", data_type="string")
    print(f"Sender ID: {sender_id}")

    # # Register callbacks
    # print("Registering callbacks...")
    # await corelink.register_callback(callback, "data")
    # await corelink.register_callback(subscriber, "subscriber")
    # await corelink.register_callback(dropped, "dropped")
    # await corelink.register_callback(update, "update")
    # await corelink.register_callback(stale, "stale")

    print("Start receiving frames...")
    connection_check = asyncio.create_task(check_connection())

    # OpenCV VideoCapture
    print("Opening camera...")
    cap = cv2.VideoCapture(0)  # Open default camera
    if not cap.isOpened():
        raise RuntimeError("Failed to open camera")

    try:
        frame_counter = 0
        print("Starting frame capture loop...")
        while True:
            # Read frame
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                await asyncio.sleep(0.1)
                continue

            # Encode frame to JPEG bytes
            success, jpeg_data = cv2.imencode('.jpg', frame)
            if not success:
                print("Failed to encode frame")
                continue

            # Convert to bytes (this was the issue in your code)
            frame_bytes = jpeg_data.tobytes()
            
            # Send the frame
            await send_file(frame_bytes, frame_counter)
            
            print(f"Frame {frame_counter} sent ({len(frame_bytes)} bytes)")
            frame_counter += 1

            # Control frame rate
            await asyncio.sleep(0.033)  # ~30 FPS
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        print("Releasing camera...")
        cap.release()

    await send_end_message()
    connection_check.cancel()

    print("Main loop completed")

# Run it
if __name__ == "__main__":
    print("Starting application...")
    try:
        corelink.run(main())
    except KeyboardInterrupt:
        print("Application terminated by user")
    except Exception as e:
        print(f"Application terminated due to error: {e}")
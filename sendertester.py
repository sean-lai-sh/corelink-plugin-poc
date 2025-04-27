import time
import numpy as np
import sys
sys.path.append("C:/Users/seanl/HSRN/corelink-pyclient/python/package/Corelink/src")
import corelink

def generate_permutations(s):
    # Base case: if the string is empty or a single character, return it as the only permutation.
    if len(s) <= 1:
        return [s]

    permutations = []
    
    # Loop through every character in the string
    for i, char in enumerate(s):
        # Form a new string without the current character
        remaining = s[:i] + s[i+1:]
        
        # Recursively generate all permutations of the remaining string
        for perm in generate_permutations(remaining):
            permutations.append(char + perm)
    
    return permutations

async def main():
    await corelink.connect("Testuser", "Testpassword", "127.0.0.1", "20012")
    # Open a websocket socket connection to the server (20012 refers to Secure WS Control Channel)
    senderID = await corelink.create_sender("Holodeck", "tcp", "testing", metadata="cv2imgin",data_type="string") # Holodeck is the name of the stream and udp is the type of stream
    # Alloc data struct to map stream to stream Type
    
    print("sender ID is ",senderID)
    print("waiting to send...")
    count = 0
    myDataString = "hello"
    perms = generate_permutations(myDataString)
    while True:
        # gen rand int from 0 to len(perms) -1
        actNum = np.random.randint(0, len(perms) - 1)
        print("actNum is ", actNum, " and perms[actNum] is ", perms[actNum]) 
        # we wanted some variability to test the system
        await corelink.send(senderID, perms[actNum], {"count": count}) # TODO: Investigate further why ASYNC 
        # Send data to the data channel , loop through queue and map to streamType and relay to subscriber
        count = count + 1
        if (count > 10):
            time.sleep(10000)
            count = 0


corelink.run(main())

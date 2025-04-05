## Sean Lai
### Example Workflow before plugin segmentation.
import sys 
from dotenv import load_dotenv
import os
load_dotenv()
sys.path.append(os.getenv("CL_EXP_PATH"))

import corelink
import numpy as np

from corelink import processing

import base64

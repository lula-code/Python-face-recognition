#!/usr/bin/python
# -*- coding: utf-8 -*-

# TEST-SKRIPT 
# In diesem Test-Skript werden alle benötigten Funktionen getestet.

import face_recognition
import numpy as np
import requests
import json
import time
import os
from datetime import datetime
import picamera


camera = picamera.PiCamera()
camera.resolution = (320,240)
output = np.empty((240, 320, 3), dtype=np.uint8)


# Initialize some variables
face_locations = []
face_encodings = []
print("Bitte vor die Kamera stellen und rein blicken.")
while True:
    #print ('Capturing image')

    # Grab a single frame of video from the RPi camera as a numpy array
    camera.capture(output, format='rgb')
    #camera.capture(os.getcwd()+"/"+ time.strftime("%Y%m%d-%H%M%S")+".jpg")
    #print(os.getcwd()+"/"+ time.strftime("%Y%m%d-%H%M%S")+".jpg")
    # Find all the faces and face encodings in the current frame of video

    face_locations = face_recognition.face_locations(output)
    if len(face_locations) > 0:
        print("Test erfolgreich")
        quit()
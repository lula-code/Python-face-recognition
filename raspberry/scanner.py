#!/usr/bin/python
# -*- coding: utf-8 -*-

# Dieses Skript durchsucht in einer Whiletrue Schleife durchgehend nach Gesichtern.
# Sobald Gesichter entdeckt werden, wird der Server Angefragt, ob diese Gesichter und die dazugehörigen Personen Zugriff zur Tür erhalten dürfen

# Import Settings
import config 

# Import Lib
import face_recognition
import numpy as np
import requests
import json
import time
import os
from datetime import datetime
import picamera

# fast = 1  ist schneller, fast 0 bessere quali aber langsamer
fast = 1
	
if fast == 1:
    camera = picamera.PiCamera()
    camera.resolution = (320,240)
    output = np.empty((240, 320, 3), dtype=np.uint8)
elif fast == 0:
    h = 1500 # change this to anything < 2592 (anything over 2000 will likely get a memory error when plotting
    cam_res = (int(h),int(0.75*h)) # keeping the natural 3/4 resolution of the camera
    # we need to round to the nearest 16th and 32nd (requirement for picamera)
    cam_res = (int(16*np.floor(cam_res[1]/16)),int(32*np.floor(cam_res[0]/32)))
    camera = picamera.PiCamera()
    camera.resolution = (cam_res[1],cam_res[0])
    output = np.empty((cam_res[0],cam_res[1],3),dtype=np.uint8)

# Initialize some variables

face_locations = []
face_encodings = []

while True:
    #print ('Capturing image')

    # Grab a single frame of video from the RPi camera as a numpy array
    camera.capture(output, format='rgb')
    #camera.capture(os.getcwd()+"/"+ time.strftime("%Y%m%d-%H%M%S")+".jpg")
    #print(os.getcwd()+"/"+ time.strftime("%Y%m%d-%H%M%S")+".jpg")
    # Find all the faces and face encodings in the current frame of video

    face_locations = face_recognition.face_locations(output)
    #print ('Es wurden {} Gesichter gefunden.'.format(len(face_locations)))
    face_encodings = face_recognition.face_encodings(output,face_locations)

    # Loop over each face found in the frame to see if it's someone we know.

    for face_encoding in face_encodings:
        #camera.capture(os.path.dirname(os.path.abspath(__file__))+"/mo.jpg")
        # Check faces
        # * ---------- Initialyse JSON to EXPORT --------- *
        json_to_export = {
            "APIKEY" : config.API_KEY,
            "data" : json.dumps(face_encoding.tolist())
        }

        # convert into JSON:
        a = json.dumps(json_to_export)

        # Request
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        r = requests.post("{}/check".format(config.SERVER_ADDRESS),a, headers=headers)

        # Überprüfung ob Requests 200 zurück gibt, sonst weiter
        if(r.status_code != 200):
            print("Request hat den Statuscode "+ str(r.status_code) + " und war somit nicht erfolgreich")
            continue
        # Response laden
        returnjson = json.loads(r.text)
        # Response überprüfen
        try:
            returnjson['vorname']
            returnjson['nachname']
            returnjson['access']
        except NameError:
            print("Response unvollständig")
            continue
        else:
            # Überprüfung, ob der Zugang berechtigt ist
            if returnjson['access'] == True:
                print(returnjson['vorname']+ " " + returnjson['nachname'] + " ist berechtigt einzutreten. Timer "+ datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                #
                #  OPEN THE DOOR
                # 
                print("Tür wird aufgemacht")
                # Sleep 5 seconds
                time.sleep(5)
                #
                # CLOSE THE DOOR
                #
                print("Tür wird zugemacht")
            else:
                 print(returnjson['vorname']+ " " + returnjson['nachname'] + " ist nicht berechtigt einzutreten. Timer: "+ datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


            

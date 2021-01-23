#!/usr/bin/python
# -*- coding: utf-8 -*-

# Dieses Skript ermöglicht das Hinzufügen von Gesichtern für gewisse Personen. 
# Jeder Person muss ein Name und eine ID zugewiesen werden.

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

# Counter der bereits hinzugefügten Personen
anzahlEingefuegt = 0

print("#########################################")
print("Es werden Gesichter hinzugefügt")
print("Es können mehrere Gesichter einer Person hinzugefügt werden, um die Genauigkeit zu erhöhen")
print("#########################################")
print()


# Eingabe von vorname nachname und id der person
vorname = input("Eingabe Vorname: ")
nachname = input("Eingabe Nachname: ")
person_id = input("Eingabe PersonenId: ")

print()
print("Bitte jetzt vor die Kamera stellen. Es werden Gesichter gesucht.")
print()

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

    # Grab a single frame of video from the RPi camera as a numpy array
    camera.capture(output, format='rgb')
    #camera.capture(os.getcwd()+"/"+ time.strftime("%Y%m%d-%H%M%S")+".jpg")
    #print(os.getcwd()+"/"+ time.strftime("%Y%m%d-%H%M%S")+".jpg")
    # Find all the faces and face encodings in the current frame of video

    face_locations = face_recognition.face_locations(output)
    
    # Wenn mehr als ein Gesicht , dann weiter
    if len(face_locations) > 1:
        print("Zu viele Gesicher. Bitte einzeln vor die Kamera stellen")
        continue
    #print ('Found {} faces in image.'.format(len(face_locations)))
    face_encodings = face_recognition.face_encodings(output,face_locations)

    # Loop over each face found in the frame to see if it's someone we know.

    for face_encoding in face_encodings:

        #camera.capture(os.path.dirname(os.path.abspath(__file__))+"/mo.jpg")
        # Check faces
        # * ---------- Initialyse JSON to EXPORT --------- *
        json_to_export = {
            "APIKEY" : config.API_KEY,
            "data" : json.dumps(face_encoding.tolist()),
            "id" : person_id,
            "vorname" : vorname,
            "nachname" : nachname
        }
        # convert into JSON:
        b = json.dumps(json_to_export)
        # Request
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        r = requests.post("{}/add".format(config.SERVER_ADDRESS),b, headers=headers)
        # Überprüfung ob Requests 200 zurück gibt, sonst weiter
        if(r.status_code != 200):
            print("ServerFehler - Person konnte nicht hinzugefügt werden")
            continue
        # Response laden
        returnjson = json.loads(r.text)
        
        # Überprüfung der Response
        # Es wird nur überprüft ob 'added' enthalten ist
        try:
            returnjson['added']
        except NameError:
            print("Person konnte nicht hinzugefuegt werden!")
            continue
        else:
            # Wenn added == True, dann Counter erhöhen und Nutzer benachrichtigen
            if returnjson['added']:
                anzahlEingefuegt = anzahlEingefuegt + 1
                print(str(anzahlEingefuegt) + " Gesicht wurde erfolgreich hinzugefuegt")
            else:
                # Added ist false, also was das Hinzufügen nicht erfolgreich
                print("Wurde nicht eingefuegt")
        
        # Nachfrage ob weitere Personen hinzugefügt werden sollen        
        weiterMachen = input("Weiter machen? Y/N: ")
        if(weiterMachen == "Y"):
            continue
        else:
            quit()
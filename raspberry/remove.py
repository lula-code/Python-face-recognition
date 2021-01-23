#!/usr/bin/python
# -*- coding: utf-8 -*-

# Löschung einer Person und all seiner Gesichter mittels Nachname und ID

# Import Settings
import config 

# Import Lib
import requests
import json


# Counter der bereits hinzugefügten Personen
anzahlEingefuegt = 0

print("#########################################")
print("Eine Person wird mittels Nachname und ID gelöscht")
print("Alle gespeicherten Gesichter der Person werden gelöscht")
print("#########################################")
print()


# Eingabe von nachname und id der person
nachname = input("Eingabe Nachname: ")
person_id = input("Eingabe PersonenId: ")

print()
print("Die Person mit dem Nachnamen {} und der ID {} wird gelöscht.".format(nachname, person_id))
print()


# Daten In ein Dictionary
json_to_export = {
    "APIKEY" : config.API_KEY,
    "id" : person_id,
    "nachname" : nachname
}
# convert into JSON:
b = json.dumps(json_to_export)

headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
r = requests.post("{}/delete".format(config.SERVER_ADDRESS),b, headers=headers)
# Überprüfung ob Requests 200 zurück gibt, sonst weiter
if(r.status_code != 200):
    print("Der Löschversuch war nicht erfolgreich")
    quit()
# Response laden
returnjson = json.loads(r.text)

try:
    returnjson['deleted']
except NameError:
    print("Der Löschversuch war nicht erfolgreich")
    quit()
else:
    # Wenn added == True, dann Counter erhöhen und Nutzer benachrichtigen
    if returnjson['deleted']:
        print("Die Person wurde erfolgreich gelöscht")
    else:
        # Added ist false, also was das Hinzufügen nicht erfolgreich
        print("Der Löschversuch war nicht erfolgreich")
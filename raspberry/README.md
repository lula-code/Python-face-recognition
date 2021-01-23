# Raspberry Pi



### Was wird gemacht?

Der Raspberry wird grundlegend eingerichtet, sodass die face_recognition Bibliothek genutzt werden kann. Anschließend wird der Raspberry so konfiguriert, dass er als Kamera fungiert, welche permanent Gesichter sucht. Falls ein Gesicht erkannt wurden ist,wird der Server abfragt ob diese Personen zu XXX zugriff erhalten darf. 

### Was wird gebraucht?

- Raspberry (> V3) + SD Karte
- Raspberry Kamera

### Installation

1. Raspberry OS auf die SD Karte installieren (z.b. mit dem Raspberry Pi Imager: https://www.raspberrypi.org/software/) 

2. Kamera an den Raspberry anschließen

3. SD Karten in den Raspberry stecken und booten und die Starteinstellung vornehmen (username / password ist `pi` / `raspberry`)

4. Netzwerk Verbindung  mit Lan oder WLan aufbauen

5. Kamera aktivieren

    Den Befehl:`sudo raspi-config` nutzen und die Kamera aktiveren. Nach der Aktivierung muss ein Reboot durchgeführt werden

   Ausführliche PiCamera Anleitung: https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/4

6. SSH aktivieren (optional, aber sinnvoll)

   Nutze die Befehle: `sudo systemctl start ssh` & `sudo systemctl enable ssh`, um eine SSH-Verbindung zu erlauben.

7. Benötigte Pakete installieren

   ```
   sudo apt-get update
   sudo apt-get upgrade
   sudo apt-get install build-essential \
       cmake \
       gfortran \
       git \
       wget \
       curl \
       graphicsmagick \
       libgraphicsmagick1-dev \
       libatlas-base-dev \
       libavcodec-dev \
       libavformat-dev \
       libboost-all-dev \
       libgtk2.0-dev \
       libjpeg-dev \
       liblapack-dev \
       libswscale-dev \
       pkg-config \
       python3-dev \
       python3-pip \
       zip
   sudo apt-get clean
   
   
   sudo apt-get update
   sudo apt-get upgrade
   sudo apt-get install cmake \
       wget \
       curl \
       python3-dev \
       python3-pip \
       zip
   sudo apt-get clean
   ```

8. Virtual Environment installieren mittels:`sudo apt install python3-venv`

9. Im Ordner `python` befinden sich alle benötigten Dateien, welche in einem Projektordner auf den Raspberry Pi kopiert werden müssen. Der Pfad zum Projektordner wird im weiteren Verlauf {ProjektDir} genannt.

10. Ein Virtual Environment im Projektordner einrichten mittels: `python3 -m venv {ProjektDir}/pienv ` (pienv ist der Name des Virtual Environments und kann auch ungenannt werden)

11. Mittels `cd {ProjektDir}` in Projektordner wechseln und mittels  `source pienv/bin/activate` das Virtual Environment aktivieren.

12. Alle für das Projekt benötigten Python-Bibliotheken werden automatisch mittels `pip3 install requirements.txt` installiert. 

   Liste der benötigten Python-Bibliotheken:

```
   	pip3 install numpy
   	pip3 install dlib
   	pip3 install requests
   	pip3 install face_recognition
   	pip3 install picamera
```

13. Die Parameter in der Datei `{ProjektOrdner}/config.py` anpassen.
14. Testen der Umgebung mittels: ``python3 {ProjektDir}/testAll.py`
    - Wenn keine Fehler auftreten, sucht das Skript nach Gesichtern, welche über die Kamera aufgenommen werden.

### Skripte

- `addface.py` 
  - Dieses Skript wird genutzt, um neue Gesichter zur Datenbank hinzuzufügen.
- `scanner.py` 
  - Sucht in Dauerschleife nach Gesichtern vor der Kamera und fragt den Server an ob diese Person Zugang zur Tür erhalten dürfen.
  - Nur nach erfolgreicher Verifikation durch den Server wird der Zugang gewährt

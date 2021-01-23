# Python face_recognition Projekt



Dieses Projekt entstand im Rahmen des Moduls: "Seminar Information System Planning - Current Issues" an der Friedrich-Schiller-Universität Jena im WS20/21

### Akteure

- WS20/21 
  - Erster Prototyp von:
    - Moritz Karsch
    - Dario Dubberstein
    - Torben Aaron Ukena



### Ziel des Projekts?

Es soll eine Gesichtserkennung mithilfe eines Raspberry Pi und einem Linux Server umgesetzt werden.

Hierbei kann eine neue Person und dessen Gesicht über den Raspberry Pi und einer Kamera auf dem Server registriert werden.

Ebenfalls soll der Raspberry Pi die Möglichkeit besitzen eine Gesicht vom Server verifizieren zu lassen.

Nach erfolgreicher Verifikation eines Gesichtes, soll beispielhaft eine Tür geöffnet werden.

Das Projekt ist grundlegend in Python umgesetzt.

Um Gesichter im Frame zu finden und diese auszuwerten, wird die Python Bibliothek "face-detection" eingesetzt. 

face-detection: https://pypi.org/project/face-recognition/

### Was wird gebraucht?

- Raspberry (> V3)
- Raspberry Kamera (Beispiel: https://www.raspberrypi.org/products/camera-module-v2/)
- Linux Server (für dieses Projekt wurde eine Linux-Ubuntu-VM genutzt)
- (optional) irgendwas was geöffnet/aktiviert wird, wenn eine Person erfolgreich erkannt wird und Zugriff zu irgendwas bekommt

### Einrichtung

1. Raspberry einrichten und konfigurieren (dafür bitte in den Raspberry Ordner gehen und die ReadMe folgen)
2. Server einrichten und konfigurieren (dafür bitte in den Server Ordner gehen ReadMe folgen)
3. Testen und Spaß haben

### Info

- Das ist ein reines Projekt zum testen der face_recognition Bibliothek. Das Projekt sollte so nicht genutzt werden, um produktiv eingesetzt zu werden!


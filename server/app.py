from flask import Flask, request, abort, jsonify
import face_recognition
import mysql.connector
from mysql.connector import Error
import json
import numpy as np
import config
import hashlib

# Diese Flask-Rest-API bietet 3 Endpunkte an:
# 1.Endpunkt: add -> Mit diesem Endpunkt werden Personen und ihr Gesicht hinzugefügt
# 2.Endpunkt: check ->  Ein Gesicht wird dahingehend überprüft, ob es Zugang erhalten darf oder nicht
# 3.Endpunkt: delete -> Eine Person und all ihre Gesichter werden gelöscht

app = Flask(__name__)

def checkApiKey(apikey):
    # Überprüfung ob der API gültig ist
    mydb = createDBCon()
    cursor = mydb.cursor()
    sql = "SELECT count(*) FROM `valid_device` WHERE api_key = MD5(%s);"
    val = apikey
    cursor.execute(sql, (val,))
    result = cursor.fetchone()
    cursor.close()
    mydb.close()
    if result[0] < 1:
        return False
    return True


def createDBCon():
    # DB Connection erstellen
    try:
        mydb = mysql.connector.connect(
        host=config.DBHost,
        user=config.DBUser,
        password=config.DBPassword,
        database=config.DBTable
        )
        return mydb
    except mysql.connector.Error as err:
        return False

# Mit diesem Endpunkt können Personen und Gesichter hinzugefügt werden
# Wenn eine Person bisher umbekannt ist wird ihre Person ebenfalls angelegt.
# Falls die Person bereits bekannt ist wird nur ihr Gesicht hinzugefügt.
# Pro Person können auch mehrere Gesichter hinzugefügt werden, um die Genauigkeit zu erhöhen
# Es wird ein Hash Wert des Gesichtsstring in der DBTabelle gesichter_hash abgelegt. 
# Hiermit kann überprüft werden, ob Gesichtsdaten in der gesichter DBTabelle abgeändert worden sind. 
@app.route('/add', methods=['POST'])
def addImage():
    if not request.json or 'id' not in request.json or 'data' not in request.json or 'vorname' not in request.json or 'nachname' not in request.json or 'APIKEY' not in request.json:
        return jsonify({'Error': "Postparameter sind unvollständig" }), 400
    # APIKEY check
    if not checkApiKey(request.json['APIKEY']):
        return jsonify({'Error': "APIKey ungültig" }), 401
    # Json data to var
    id = request.json['id']
    data = request.json['data']
    vorname = request.json['vorname']
    nachname = request.json['nachname']

    # Create db con
    mydb = createDBCon()
    if not mydb:
        mydb.close()
        return jsonify({'Error': "Datenbankverbindung konnte nicht hergestellt werden" }), 500

    # Abfrage, ob es die Person schon gibt in der DB
    try:
        # Create db cursor
        cursor = mydb.cursor()
        # Ist User schon in der DB?
        sql = "SELECT count(*) as count FROM personen WHERE id = %s"
        val = id
        cursor.execute(sql, (val,))
        result = cursor.fetchone()
    except mysql.connector.Error as err:
        mydb.close()
        return jsonify({'Error': "Persondendatenbank konnte nicht abgefragt werden" }), 500
    
    # Wenn result[0] < 1 dann gibt es die Person noch nicht und sie wird angelegt
    if result[0] < 1:
        try:
            # Alle Daten zur Person zur DB hinzufügen
            cursor = mydb.cursor()
            sql = "INSERT INTO personen (id,vorname,nachname) VALUES (%s,%s,%s)"
            val = (id, vorname, nachname)
            cursor.execute(sql, val )
            mydb.commit()
        except mysql.connector.Error as err:
            mydb.close()
            return jsonify({'Error': "Die Hinzufügung war der Person oder der Gesichter nicht erfolgreich" }), 500
    
    # Gesichtsdaten hinzufügen
    try:
        # Alle Daten  Gesicht und GesichtHash zur DB hinzufügen
        sql = "INSERT INTO gesichter (person_id, data) VALUES (%s, %s)"
        val = (id, data)
        cursor.execute(sql, val)
        sql = "INSERT INTO `gesichter_hash` (`id`, `hash`) VALUES (%s, %s)"
        val = (cursor.lastrowid, hashlib.md5(data.encode('utf-8')).hexdigest())
        cursor.execute(sql, val)
        mydb.commit()
        cursor.close()
        mydb.close()
        return jsonify({"added": True})
    except mysql.connector.Error as err:
        mydb.close()
        return jsonify({'Error': "Die Hinzufügung war der Person oder der Gesichter nicht erfolgreich" }), 500
    return jsonify({"added": False})

# Ein Gesicht wird dahingehend überprüft, ob es Zugang erhalten darf oder nicht
# Wenn ein Match gefunden worden ist, wird geprüft ob der Match durch abgeänderte Gesichtsdaten zustande kam. 
# Hierfür wird ein Hash der Gesichtsdaten erstellt und mit dem dazugehörigen Hash in der gesichter_hash DBTabelle abgeglichen     
@app.route('/check', methods=['POST'])
def checkImage():
    if not request.json or 'data' not in request.json or 'APIKEY' not in request.json:
        return jsonify({'Error': "Postparameter sind unvollständig" }), 400

    # APIKEY check   
    if not checkApiKey(request.json['APIKEY']):
        return jsonify({'Error': "APIKey ungültig" }), 401

    # Json data to var
    data = request.json['data']

    ## Data to np array
    k = np.array(json.loads(data))

    # Create db con
    mydb = createDBCon()
    if not mydb:
        return jsonify({'Error': "Datenbankverbindung konnte nicht hergestellt werden" }), 500

    # Holen aller Gesichtsdaten, um mittels face_recognition.compare_faces die Gesichter zu vergleichen
    try:
        cursor = mydb.cursor()
        sql = "SELECT CONVERT(data USING utf8), person_id, id FROM gesichter"
        cursor.execute(sql)
        result = cursor.fetchall()
    except mysql.connector.Error as err:
        mydb.close()
        return jsonify({'Error': "Datenbankfehler, bei abholen aller Gesichter"}), 500

    # Wenn keine Gesichtsdaten in der DBTablelle sind kann sofort ein Fehler zurückgegeben werden
    if len(result) < 1:
        mydb.close()
        return jsonify({'Error': "Aktuell sind keine Gesichter in der Datenbank" }), 400
   
    # Jedes Gesicht aus der DB mit dem Gesicht aus dem Request abgleichen
    # Ingesamt ist dieser Part bei vielen Gesichtern nicht gerade performant 
    for x in result:
        returnjson = json.loads(x[0])
        l = np.array(returnjson)
        match = face_recognition.compare_faces([l, l],k)
        
        if match[0]:
                # Überprüfe ob der Hash der Geischter noch übereinstimmt
                try:
                    sql = "SELECT count(*) FROM `gesichter` as a INNER JOIN gesichter_hash as b ON (MD5(CONVERT(a.data USING utf8)) = b.hash) WHERE a.id = %s"
                    cursor.execute(sql, (x[2], ))
                    count = cursor.fetchone()
                except mysql.connector.Error as err:
                    cursor.close()
                    mydb.close()
                    return jsonify({'Error': "Datenbankfehler beim dem Abgleich der Gesichtsdaten" }), 400
                
                # wenn der counter < 1 ist, wurde die Gesichtsdaten nachträglich abgeändert
                if count[0] < 1:
                    cursor.close()
                    mydb.close()
                    return jsonify({'Error': "Es wurden Gesichtsdaten abgeändert, um Zugriff zu erhalten!" }), 400

                # Person zum passenden Gesicht raussuchen
                try:
                    sql = "SELECT vorname, nachname FROM personen WHERE id = %s"
                    cursor.execute(sql, (x[1],))
                    resultPerson = cursor.fetchone()
                    return json.dumps({'vorname': resultPerson[0], 'nachname': resultPerson[1], 'access': True})
                except mysql.connector.Error as err:
                    mydb.close()
                    return jsonify({'Error': "Personendaten zu einem passenden Gesicht konnten nicht abgerufen werden" }), 400
    mydb.close()
    return jsonify({'Error': "Kein passenden Gesicht gefunden" }), 400

# Eine Person und all ihre Gesichter werden gelöscht
# Die Person wird aus personen gelöscht.
# Alle dazugeörigen Gesichter werden aus gesichter und gesichter_hash gelöscht
@app.route('/delete', methods=['POST'])
def deletePerson():
    if not request.json or 'id' not in request.json or 'nachname' not in request.json  or 'APIKEY' not in request.json:
        return jsonify({'Error': "Postparameter sind unvollständig" }), 400

    # APIKEY check   
    if not checkApiKey(request.json['APIKEY']):
        return jsonify({'Error': "APIKey ungültig" }), 401

    # Json data to var
    id  = request.json['id']
    nachname  = request.json['nachname']

    # Create db con
    mydb = createDBCon()
    if not mydb:
        return jsonify({'Error': "Datenbankverbindung konnte nicht hergestellt werden" }), 500

    # Die zu löschende Person in der Datenbank suchen 
    try:
        # Create db cursor
        cursor = mydb.cursor()
        sql = "SELECT count(*) FROM personen WHERE id = %s AND nachname = %s"
        cursor.execute(sql, (id, nachname))
        result = cursor.fetchone()
    except mysql.connector.Error as err:
        mydb.close()
        return jsonify({'Error': "Datenbankfehler, bei der suche der zu löschenden Person" }), 500

    if result[0] != 1:
        mydb.close()
        return jsonify({'Error': "Diese Person ist nicht in der Datenbank" }), 400
    
    # Alle ids aller Gesichter von der Person
    try:
        # Create db cursor
        cursor = mydb.cursor()
        sql = "SELECT id FROM gesichter WHERE person_id = %s"
        cursor.execute(sql, (id, ))
        result = cursor.fetchall()
    except mysql.connector.Error as err:
        mydb.close()
        return jsonify({'Error': "Die zu löschenden Gesichter konnten nicht aus der Datenbank abgefragt werden" }), 500
        abort(400)

    for x in result:
        # Lösche die x[0] id von gesichter und von gesichter_hash
        try:
            sql = "DELETE FROM `personen` WHERE id = %s AND nachname = %s"
            cursor.execute(sql, (id,nachname ))
            sql = "DELETE FROM `gesichter` WHERE id = %s"
            cursor.execute(sql, (x[0], ))
            sql = "DELETE FROM `gesichter_hash` WHERE id = %s"
            cursor.execute(sql, (x[0], ))
            mydb.commit()
        except mysql.connector.Error as err:
            return jsonify({'Error': "Löschvorgang nicht erfolgreich" }), 500

    cursor.close()
    mydb.close()
    return jsonify({"deleted": True})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

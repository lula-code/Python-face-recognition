# Server



### Was wird gemacht?

Der Server hat die Aufgabe eine REST-API anzubieten mit folgenden Funktionen:

- Gesichter für bestimmte Personen hinzufügen
- Überprüfen ob ein Gesicht in der Datenbank ist und somit die Person Zugriff auf z.b. eine Tür bekommen darf
- Person und all ihre Gesichter löschen

### Was wird gebraucht?

- Ein Linux Server (z.b. in einer VM)

### Installation

1. Ubuntu Server installieren (z.b. Ubuntu Server 20.04.1 LTS : https://ubuntu.com/download/server) und bei der Installation alles notwendige wie SSH aktivieren. In dieser Anleitung wurde hierbei der User `faceserver` angelegt.

2. SSH aktivieren, wenn nicht bei der Installation gemacht:
```
   	sudo apt update && sudo apt install openssh-server && sudo systemctl status ssh && sudo ufw allow ssh
```

3. Paar  notwendige Module installieren (Liste kann noch gekürzt werden)

   ```
   sudo apt-get -y install gfortran && sudo apt-get -y install git && sudo apt-get -y install wget && sudo apt-get -y install curl && sudo apt-get -y install graphicsmagick && sudo apt-get -y install libgraphicsmagick1-dev && sudo apt-get -y install libatlas-base-dev && sudo apt-get -y install libavcodec-dev && sudo apt-get -y install libavformat-dev && sudo apt-get -y install libboost-all-dev && sudo apt-get -y install libgtk2.0-dev && sudo apt-get -y install libjpeg-dev && sudo apt-get -y install liblapack-dev && sudo apt-get -y install libswscale-dev && sudo apt-get -y install pkg-config && sudo apt-get -y install python3-dev && sudo apt-get -y install python3-numpy && sudo apt-get -y install python3-pip && sudo apt-get -y install zip  && pip3 install scikit-image && sudo apt-get -y install python3-scipy && sudo apt-get -y install libatlas-base-dev && sudo apt-get -y install libjasper-dev && sudo apt-get -y install libqtgui4 && sudo apt-get -y install python3-pyqt5 && sudo apt install libqt4-test && sudo apt-get install build-essential && sudo apt-get install cmake
   ```

4. Python REST-API installieren

   1. Apache installieren

       ```
       sudo apt install apache2
       sudo ufw allow 'Apache'
       sudo ufw status
       sudo systemctl status apache2 (sollte nun aktiviert sein | q drücken, um wieder raus zu kommen)
       ```

   2. Python Projekt anlegen und ein Virtual Environment anlegen

      ```
   sudo apt install python3-venv
        cd {ProjektOberOrdner}
        mkdir {ProjektOrdnerName}
        cd {ProjektOrdnerName}
        python3 -m venv flaskvenv
        source flaskvenv/bin/activate
        
      ```
      
    3. Alle Bibliotheken installieren mittels `pip3 install requirements.txt`

    4. Rest-API Skript anlegen | Ist nur zum erstellen und da, wird später durch das richtige Skript ersetzt

        ```
       nano app.py
       ```

        ```
        from flask import Flask, request, abort, jsonify
        
        app = Flask(__name__)
       
        @app.route('/getSquare', methods=['POST'])
            def get_square():
                if not request.json or 'number' not in request.json:
                    abort(400)
            num = request.json['number']
            return jsonify({'answer': num ** 2})
            
         if __name__ == '__main__':
            app.run(host='127.0.0.1', port=8080, debug=True)
        
        ```

    5. Gunicorn einrichten

        1. `wsgi.py` mit `nano {ProjektOrdner}/wsgi.py` öffnen und folgendes einfügen:
        
            ```
        from app import app
            
            if __name__ == '__main__':
                app.run()
            ```
       
        2. Die IP `127.0.0.1:8080` auf die App binden:

            ```
             gunicorn --bind 127.0.0.1:8080 wsgi:app
            ```
   3. gunicorn mit Strg + C schließen und das ENV mit `deactivate` schließen
        
        4. `{ProjektOrdner}/nano gunicorn_config.py` öffnen und folgendes einsetzen:
        
       ```
        import multiprocessing
            
            workers = multiprocessing.cpu_count() * 2 + 1
        bind = 'unix:flaskrest.sock'
        umask = 0o007
            reload = True
            #logging
                accesslog = '-' ###############
                errorlog = '-'  #################
            ```
        
    6. Flask Service einrichten

        ```
        sudo nano /etc/systemd/system/flaskrest.service
        ```

        - SERVERUSER ersetzen!

        ```
        [Unit]
        Description=Gunicorn instance to serve flask application
        After=network.target
        
        [Service]
         User=SERVERUSER
        Group=www-data
         WorkingDirectory=/home/faceserver/flask_rest/
        Environment="PATH=/home/faceserver/flask_rest/flaskvenv/bin"
         ExecStart=/home/faceserver/flask_rest/flaskvenv/bin/gunicorn --config gunicorn_config.py wsgi:app
        
        [Install]
        WantedBy=multi-user.target
        ```

        - Aktiveren und Status anschauen

          ```
           sudo systemctl start flaskrest.service
           sudo systemctl enable flaskrest.service
           sudo systemctl status flaskrest.service
          ```

        - flaskrest.conf Datei bearbeiten

          ```
          sudo nano /etc/apache2/sites-available/flaskrest.conf
          ```

        - Folgendes eintragen und die jeweilige IP Adresse des Servers passend setzen

          ```
           <VirtualHost *:80>
           ServerName {IPAdresseDesServers/Proxy}
               ErrorLog ${APACHE_LOG_DIR}/flaskrest-error.log
           CustomLog ${APACHE_LOG_DIR}/flaskrest-access.log combined
               <Location />
                   ProxyPass unix:/home/faceserver/flask_rest/flaskrest.sock|http://127.0.0.1/
                   ProxyPassReverse unix:/home/faceserver/flask_rest/flaskrest.sock|http://127.0.0.1/
               </Location>
           </VirtualHost>
          ```

        - Apache neu starten und Proxyeinstellungen setzen

          ```
          sudo a2enmod proxy
          sudo a2enmod proxy_http
          sudo a2enmod proxy_connect
          sudo a2ensite flaskrest.conf
          sudo systemctl reload apache2
          ```

          

5. MYSQL Datenbank installieren (https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04-de)

    ```
    sudo apt update
    sudo apt install mysql-server
    ```

    - MYSQL Server konfigurieren:

    ```
    sudo mysql_secure_installation
    ```

    - Root User ein neues Passwort geben. Es kann auch ein neuer User hierfür angelegt werden

    ```
    sudo mysql
    ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';
    exit;
    ```

    Mysql kann ab jetzt immer mit folgenden Code aufgerufen werden

    ```
    mysql -u root -p
    ```

    Testen mit:

    ```
    systemctl status mysql.service
    ```

    Projekt DB anlegen und das Dump-File einspielen

    ```
    mysql -u root -p
    ```

    ```
    create database if not exists faceprojekt;
    ```

    ```
    use faceprojekt;
    ```

    ```
    source {PROJEKTDIR}/db.dump
    ```
    
6. Apache2 neu starten

    ```
    sudo a2ensite flaskrest.conf
    sudo systemctl reload apache2
    ```

7. ``{ProjektOrdner}/app.py ` mit der der `app.py` aus diesem **Repository** ersetzen

8. Die Parameter in der Datei `{ProjektOrdner}/config.py` anpassen.

### Endpunkte

Die RestApi bietet folgende 3 Endpunkte an:

1.Endpunkt: add (POST) -> Mit diesem Endpunkt werden Personen und ihr Gesicht hinzugefügt

2.Endpunkt: check (POST) -> Ein Gesicht wird dahingehend überprüft, ob es Zugang erhalten darf oder nicht

3.Endpunkt: delete (POST) -> Eine Person und all ihre Gesichter werden gelöscht

### Testen

Mit folgenden Requests können die jeweiligen Endpunkte getestet werden. Hierbei ist auch ersichtlich welche Informationen die Endpunkte zum bearbeiten benötigen:

1.  add 

   ```
   curl --location --request POST 'http://URL/add' \
   --header 'Content-Type: application/json' \
   --data-raw '{"APIKEY": "6ce76f32-7bdd-4150-a288-3db493645449", "data": "[-0.1419695019721985, 0.06507774442434311, 0.008559349924325943, -0.01635592058300972, -0.06743860989809036, -0.020224709063768387, -0.022186974063515663, -0.14794978499412537, 0.07495485991239548, -0.06320060044527054, 0.2398945391178131, -0.030264761298894882, -0.24406678974628448, -0.11075858771800995, 0.07020332664251328, 0.0470847487449646, -0.06467069685459137, -0.14498357474803925, -0.16332101821899414, -0.02453750930726528, 0.012378035113215446, -0.018366431817412376, -0.0409538596868515, 0.09153904765844345, -0.22377783060073853, -0.2192050665616989, -0.08601050823926926, -0.09280036389827728, 0.09123386442661285, -0.12796343863010406, 0.06308630853891373, 0.058903492987155914, -0.11475317180156708, -0.030873049050569534, 0.013510357588529587, 0.11584103107452393, -0.09292252361774445, -0.06161848083138466, 0.2843742370605469, -0.09075096249580383, -0.14859643578529358, -0.060670241713523865, 0.028030680492520332, 0.27811476588249207, 0.1991819590330124, -0.0023589825723320246, 0.08326172828674316, -0.06759168207645416, 0.10776453465223312, -0.24505820870399475, 0.07584266364574432, 0.12255740910768509, 0.09489057958126068, 0.14379499852657318, 0.05390341579914093, -0.23018713295459747, 0.07787039875984192, 0.16709508001804352, -0.17929625511169434, 0.14305345714092255, 0.03624885156750679, -0.21280232071876526, -0.0591132715344429, 0.0005893390625715256, 0.17986516654491425, 0.04146246984601021, -0.07071711122989655, -0.18516594171524048, 0.18525052070617676, -0.20009252429008484, -0.0706973522901535, 0.15841367840766907, -0.10755598545074463, -0.1714361011981964, -0.32292670011520386, 0.03072476014494896, 0.3378961384296417, 0.15228021144866943, -0.23825132846832275, 0.022930003702640533, 0.0061299558728933334, -0.04150637984275818, 0.10695657134056091, 0.03269165754318237, -0.050870973616838455, -0.14965100586414337, -0.1511537879705429, 0.016854802146553993, 0.27991166710853577, 0.0019708052277565002, 0.016733046621084213, 0.17970257997512817, 0.0882641077041626, -0.05591549351811409, 0.07686301320791245, 0.020475301891565323, -0.06846445798873901, -0.008732868358492851, -0.03147846832871437, 0.04133298248052597, 0.11822564899921417, -0.10210771858692169, 0.048204075545072556, 0.09557848423719406, -0.14859068393707275, 0.27453142404556274, 0.016372105106711388, 0.023049190640449524, 0.017000917345285416, -0.0656629279255867, -0.13724271953105927, -0.0016474203439429402, 0.2522275745868683, -0.2508549392223358, 0.21435600519180298, 0.161094531416893, 0.08863995969295502, 0.11352679878473282, 0.07461723685264587, 0.11939816176891327, -0.018716461956501007, 0.057101793587207794, -0.19772975146770477, -0.04633445665240288, 0.040687836706638336, -0.07169538736343384, 0.05268222093582153, 0.056859057396650314]", "id": "1", "vorname": "Moritz", "nachname": "Karsch"}
   '
   ```

   

2. check

   ```
   curl --location --request POST 'http://URL/check' \
   --header 'Content-Type: application/json' \
   --data-raw '{"APIKEY": "6ce76f32-7bdd-4150-a288-3db493645449", "data": "[-0.035554543137550354, 0.09642165154218674, 0.058599598705768585, -0.03474181517958641, -0.08048126101493835, 0.01918877474963665, -0.024060310795903206, -0.15142963826656342, 0.11188091337680817, -0.01926843822002411, 0.21585460007190704, -0.03890371322631836, -0.2658246159553528, -0.06480566412210464, 0.08136001229286194, 0.06488212943077087, -0.10307560861110687, -0.15051032602787018, -0.11779532581567764, 0.012846767902374268, -0.034895122051239014, -0.0015526330098509789, 0.0547233484685421, 0.04207969456911087, -0.15045899152755737, -0.2793581485748291, -0.09727618098258972, -0.15051047503948212, 0.06523855775594711, -0.116883285343647, 0.06228639930486679, 0.011010945774614811, -0.13523517549037933, -0.014825636520981789, 0.02467232011258602, 0.005899863317608833, -0.04653321951627731, -0.15782903134822845, 0.25083911418914795, -0.0838509351015091, -0.1378454566001892, -0.04870128259062767, 0.03711028769612312, 0.16617554426193237, 0.14760778844356537, -0.033665724098682404, 0.08229759335517883, -0.03759504109621048, 0.04977564886212349, -0.23935584723949432, 0.11766083538532257, 0.06731066852807999, 0.1337140053510666, 0.10510852932929993, 0.06621431559324265, -0.2179822474718094, 0.07172784954309464, 0.13073523342609406, -0.23198655247688293, 0.14960214495658875, 0.06264955550432205, -0.03335503488779068, -0.05143630504608154, 0.05454745143651962, 0.22377446293830872, 0.13579918444156647, -0.09515003859996796, -0.1762293428182602, 0.10871560871601105, -0.1665520966053009, -0.038123685866594315, 0.12979891896247864, -0.13659773766994476, -0.16569054126739502, -0.21831785142421722, 0.03529806435108185, 0.3507036864757538, 0.09668749570846558, -0.271828293800354, -0.06420229375362396, -0.03206317871809006, -0.028415851294994354, 0.0307318065315485, 0.020490121096372604, -0.07003357261419296, -0.1292097568511963, -0.1142033264040947, 0.004632081836462021, 0.2502076327800751, -0.007353911176323891, -0.05295100808143616, 0.2491236925125122, 0.03652311488986015, -0.04865449666976929, 0.0387234166264534, 0.0212684515863657, 0.017533857375383377, -0.006123090162873268, -0.023530930280685425, 0.052080463618040085, 0.08047813922166824, -0.07329186797142029, -0.035358231514692307, 0.11419343948364258, -0.17161047458648682, 0.16221275925636292, -0.0009465257171541452, -0.03319200500845909, 0.03679422289133072, -0.016598472371697426, -0.1281760036945343, -0.04538419470191002, 0.23870395123958588, -0.28652268648147583, 0.20793192088603973, 0.15409256517887115, 0.06276252120733261, 0.07339942455291748, -0.029643811285495758, 0.09375736117362976, 0.06060551851987839, 0.03142476826906204, -0.15067856013774872, -0.06074101850390434, 0.0433274582028389, -0.06811325997114182, -0.01400437206029892, 0.054113712161779404]"}
   ```

   

3. delete

   ```
   curl --location --request POST 'http://URL/delete' \
   --header 'Content-Type: application/json' \
   --data-raw '
   {"APIKEY": "6ce76f32-7bdd-4150-a288-3db493645449", "id": "1", "nachname": "NAME"}
   '
   ```

   


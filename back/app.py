import threading,time,smbus,datetime
from RPi import GPIO
from flask import Flask, jsonify, request, url_for, json
from flask_cors import CORS
from mfrc522 import SimpleMFRC522
from flask_socketio import SocketIO
from subprocess import check_output
from klasses import I2C_LCD_driver

time.sleep(60)

# Custom imports
from database.DP1Database import Database

# Start app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
conn = Database(app=app, user='mct', password='mct', db='secretdoor')

# Custom endpoint
endpoint = '/api/v1'

#GPIO SETUP
mylcd = I2C_LCD_driver.lcd()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

fotopin = 20
GPIO.setup(fotopin, GPIO.IN)
GPIO.input(fotopin)

sound = 21
GPIO.setup(sound, GPIO.IN)
GPIO.input(sound)

reader = SimpleMFRC522()

fase1 = False
fase2 = False

gebruiker = 1
teller = 0

#LCD--------------------------------------------------------------------------------------------------------

def ophalenIP():
    ips = check_output(['hostname', '--all-ip-addresses'])
    ip = ips.split()
    ip1 = ip[0]
    print(ip1)
    return str(ip1)

mylcd.lcd_display_string(ophalenIP(), 1)

#MOTOR-------------------------------------------------------------

GPIO.setup(26,GPIO.OUT)
GPIO.output(26,1)

def motor():
    try:
        GPIO.output(26, 0)
        time. sleep(6.25 )
    except:
        print("error motor")
    finally:
        GPIO.output(26, 1)

#RFID----------------------------------------------------------------------
def RFID():
    try:
        global gebruiker,fase1
        currentDT = str(datetime.datetime.now())
        id, text = reader.read()
        print(id)
        gebruiker = text
        print(gebruiker)
        toevoegen = conn.set_data("INSERT INTO metingen(sensorid,tijdstip,waarde,idGebruiker) VALUES (%s,%s,%s,%s)",
                                      [1, currentDT, id, text])
        print(toevoegen)
        fase1 = True
        threading.Timer(3.0, RFID).start()
    except:
        print("fout bij RFID lezen")

r = threading.Timer(3.0, RFID)
r.start()

#PHOTOTRANSISTOR------------------------------------------------------------

def lees_phototransitor(fotopin):
    global fase1,fase2,gebruiker
    waarde = GPIO.input(fotopin)
    try:
        print(fase1)
        if fase1 == True:
            currentDT = str(datetime.datetime.now())
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Access", 1)
            mylcd.lcd_display_string("Granted", 2)
            print("kast opent")
            motor()
            conn.set_data("INSERT INTO metingen(sensorid,tijdstip,waarde,idGebruiker) VALUES (%s,%s,%s,%s)",
                                      [2, currentDT, "boek geactiveerd", gebruiker])
            fase2 = True
            fase1= False
            time.sleep(1)

    except:
        print("error lezen transistor")

GPIO.add_event_detect(fotopin, GPIO.RISING, bouncetime=300)
GPIO.add_event_callback(fotopin, callback=lees_phototransitor)

#Geluidsensor-----------------------------------------------------------------

def tellerdef(pin):
    global teller,fase2
    try:
        teller += 1
        print(teller)
        if teller >= 2 and fase2 == True:
            lees_geluidssensor()
            teller = 0
        if teller >= 2 and fase2 == False:
            teller = 0
    except:
        print("fout bij teller")

def lees_geluidssensor():
    global gebruiker,fase2
    print("{}".format(GPIO.input(sound)))
    if fase2 == True:
        try:
            currentDT = str(datetime.datetime.now())
            print("kast sluit")
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Closing", 1)
            motor()
            conn.set_data("INSERT INTO metingen(sensorid,tijdstip,waarde,idGebruiker) VALUES (%s,%s,%s,%s)",
                          [3, currentDT, "geluid", gebruiker])
            print("data verstuurd")
        except:
            print("error bij lezen geluid")
        finally:
            mylcd.lcd_clear()
            mylcd.lcd_display_string(ophalenIP(), 1)
            fase2 = False

GPIO.add_event_detect(sound, GPIO.RISING, bouncetime=500)
GPIO.add_event_callback(sound, callback=tellerdef)

#ROUTES-------------------------------------------------------------------------

@app.route(endpoint + '/', methods= ['GET'])
def get_test():
    if request.method == 'GET':
        try:
            print("connectie werkt")
        except():
            print(Exception)
            return 'An error occurd', 500

@app.route(endpoint + '/gebruikers', methods= ['GET'])
def get_gebruikers():
    if request.method == 'GET':
        try:
            client_data= conn.get_data('SELECT * FROM gebruiker')
            return jsonify(client_data),200
        except():
            print(Exception)
            return 'An error occurd', 500

@app.route(endpoint + '/metingen', methods= ['GET'])
def get_metingen():
    if request.method == 'GET':
        try:
            client_data= conn.get_data('SELECT * FROM metingen')
            return jsonify(client_data),200
        except():
            print(Exception)
            return 'An error occurd', 500

@app.route(endpoint + '/sensoren', methods=['GET'])
def get_sensoren():
    if request.method == 'GET':
        try:
            client_data= conn.get_data('SELECT * FROM sensoren')
            return jsonify(client_data),200
        except():
            print(Exception)
            return 'An error occurd', 500

#SOCKET--------------------------------------------------------------
@socketio.on("connect")
def connecting():
    print("Connection with client established")


@socketio.on('knop')
def lees_knop(pin):
    motor()
    print("gelukt")


if __name__ == '__main__':
    socketio.run(app, host= "0.0.0.0", port= 5000)


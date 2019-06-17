import threading,time,smbus,datetime
from RPi import GPIO
from flask import Flask, jsonify, request, url_for, json
from flask_cors import CORS
from mfrc522 import SimpleMFRC522
from flask_socketio import SocketIO

# Custom imports
from database.DP1Database import Database

#lcd---------------
I2C_adres = 0x3f #starting adres -> sudo i2cdetect -y 1
maxChar = 16 #max aantal characters

sturen_data = 1  # Mode - Sending data
sturen_command = 0  # Mode - Sending command

eersteLijn = 0x80  # LCD RAM address for the 1st line
tweedeLijn = 0xC0  # LCD RAM address for the 2nd line
lcd_achtergrond = 0x08  # aanzetten achtergrond licht
enable = 0b00000100  # Enable bit

# Open I2C interface
bus = smbus.SMBus(1)

# Start app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
conn = Database(app=app, user='mct', password='mct', db='secretdoor')

# Custom endpoint
endpoint = '/api/v1'

def lcd_init():
    lcd_byte(0x33, sturen_command)  # 110011 initialiseren
    lcd_byte(0x32, sturen_command)  # 110010 initialiseren
    lcd_byte(0x01, sturen_command)  # 000001 Clear display
    time.sleep(0.005)

def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data,0 for command

    bits_high = mode | (bits & 0xF0) | lcd_achtergrond
    bits_low = mode | ((bits << 4) & 0xF0) | lcd_achtergrond

    # High bits
    bus.write_byte(I2C_adres, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(I2C_adres, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(0.005)
    bus.write_byte(I2C_adres, (bits | enable))
    time.sleep(0.005)
    bus.write_byte(I2C_adres, (bits & ~enable))
    time.sleep(0.005)

def stuur_bericht(bericht, lijn):
    # Send string to display

    bericht = bericht.ljust(maxChar, " ")

    lcd_byte(lijn, sturen_command)

    for i in range(maxChar):
        lcd_byte(ord(bericht[i]), sturen_data)

#GPIO SETUP
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
                                      [2, currentDT, id, text])
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
            #lcd_init()
            # stuur_bericht("Acces", eersteLijn)
            # stuur_bericht("Granted", tweedeLijn)
            currentDT = str(datetime.datetime.now())
            print("kast opent")
            motor()
            conn.set_data("INSERT INTO metingen(sensorid,tijdstip,waarde,idGebruiker) VALUES (%s,%s,%s,%s)",
                                      [3, currentDT, "boek geactiveerd", gebruiker])
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
            motor()
            conn.set_data("INSERT INTO metingen(sensorid,tijdstip,waarde,idGebruiker) VALUES (%s,%s,%s,%s)",
                          [1, currentDT, "geluid", gebruiker])
            print("data verstuurd")
        except:
            print("error bij lezen geluid")
        finally:
            fase2 = False
            #lcd_byte(0x01, sturen_command)

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


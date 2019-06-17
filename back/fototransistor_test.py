from RPi import GPIO
GPIO.setmode(GPIO.BCM)
fotopin = 20
GPIO.setup(fotopin, GPIO.IN)
GPIO.input(fotopin)


def lees_phototransitor(fotopin):
    waarde = GPIO.input(fotopin)
    try:
        if waarde == 1:
            print("ok")

    except:
        print("error lezen transistor")

GPIO.add_event_detect(fotopin, GPIO.RISING, bouncetime=300)
GPIO.add_event_callback(fotopin, callback=lees_phototransitor)

while True:
    pass
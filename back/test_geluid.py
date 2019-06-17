import datetime
from RPi import GPIO

sound = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(sound, GPIO.IN)
GPIO.input(sound)


def lees_geluidssensor(sound):
    global boek
    currentDT = str(datetime.datetime.now())
    print("{}".format(GPIO.input(sound)))
    if GPIO.input(sound) == 1:
        try:
            print("kast sluit")
        except:
            print("error bij lezen geluid")


GPIO.add_event_detect(sound, GPIO.RISING, bouncetime=300)
GPIO.add_event_callback(sound, callback=lees_geluidssensor)

while True:
    pass
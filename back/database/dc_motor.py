import threading,time,smbus,datetime
from RPi import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)

GPIO.output(19, 0)
GPIO.output(26, 0)
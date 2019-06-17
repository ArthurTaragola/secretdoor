import time

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
        while True:
                id, text = reader.read()
                print(id)
                print(text)
                time.sleep(2)
finally:
        GPIO.cleanup()
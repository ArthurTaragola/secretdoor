from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(26,GPIO.OUT)
GPIO.output(26,1)

def motor():
    try:
        GPIO.output(26, 0)
        time. sleep(12.5)
    except:
        print("error motor")
    finally:
        GPIO.output(26, 1)

try:
    motor()
except:
    print("error")

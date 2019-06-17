from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(19,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)

p = GPIO.PWM(19,50)
q = GPIO.PWM(26,50)


p.start(0)
q.start(0)

def motor():
    try:
        p.ChangeDutyCycle(100)
        time. sleep(2)
        p.ChangeDutyCycle(0)
    except:
        print("error motor")
    finally:
        p.ChangeDutyCycle(0)
        q.ChangeDutyCycle(0)

try:
    motor()
except:
    print("error")

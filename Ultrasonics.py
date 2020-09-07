#!/usr/bin/python3
# -*- coding:utf-8 -*-
import time
from RPi import GPIO


def _setup():
    ECHO = 19
    TRIG = 17
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.setup(TRIG, GPIO.OUT)

def biu():
    ECHO = 19
    TRIG = 17
    
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(1e-3)

    # trigger
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(15e-6)
    GPIO.output(TRIG, GPIO.LOW)

    # echo
    while GPIO.input(ECHO) == 0:
        pass
    start = time.time()

    while GPIO.input(ECHO) == 1:
        pass
    finish = time.time()

    GPIO.setup(ECHO, GPIO.OUT)
    GPIO.output(ECHO, GPIO.LOW)
    GPIO.setup(ECHO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    distance = 1e3*(finish-start)*340/2

    return distance # in mm


if __name__ == '__main__':
    _setup()
    while True:
        try:
            distance = biu()
            print('{:12.2f} mm'.format(distance))
            time.sleep(1)
        except KeyboardInterrupt:
            GPIO.cleanup()
            break

#!/usr/bin/python3
# -*- coding:utf-8 -*-
import time
import picamera
from RPi import GPIO

def biii(frequency, duration):
    freq = frequency
    if not freq == 0:
        interval = 1/freq
        num = 0
        while True:
            if num >= duration*freq:
                break
            num += 1
            GPIO.output(17, GPIO.HIGH)
            time.sleep(interval/2)
            GPIO.output(17, GPIO.LOW)
            time.sleep(interval/2)
    else:
        time.sleep(duration)

def _setup():
    buzzer = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzzer, GPIO.OUT)

if __name__ == '__main__':
    _setup()
    
    camera = picamera.PiCamera()

    time.sleep(5)
    biii(653, 0.1)
    time.sleep(0.1)
    camera.capture('example.jpg')
    '''
    biii(653, 0.3)
    time.sleep(0.3)
    camera.start_recording('example.h264')
    time.sleep(5)
    camera.stop_recording()
    '''
    camera.close()
    GPIO.cleanup()

#!/usr/bin/python3
# -*- coding:utf-8 -*-
import time
import numpy as np
import RPi.GPIO as GPIO


def _setup():
    BtnPin = 19
    Gpin = 5
    Rpin = 6
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
    GPIO.setup(Gpin, GPIO.OUT)     # Set Green Led Pin mode to output
    GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)

def sine(pin,value):
    x = 0
    y = 0.99*np.sin(x)+1
    while GPIO.input(BtnPin) == value:
        t_on = 0.01*y
        t_off = 0.01*(2-y)
        GPIO.output(pin,GPIO.HIGH)
        time.sleep(t_on)
        GPIO.output(pin,GPIO.LOW)
        time.sleep(t_off)
        x += np.pi/100
        y = 0.99*np.sin(x)+1

if __name__ == '__main__':
    BtnPin = 19
    Gpin = 5
    Rpin = 6
    
    _setup()
    try:
        while True:
            if GPIO.input(BtnPin) == True:
                time.sleep(0.01)
                if GPIO.input(BtnPin) == True:
                    #GPIO.output(Rpin,GPIO.HIGH)
                    #GPIO.output(Gpin,GPIO.LOW)
                    sine(Rpin,GPIO.input(BtnPin))
            elif GPIO.input(BtnPin) == False:
                time.sleep(0.01)
                if  GPIO.input(BtnPin) == False:
                    while GPIO.input(BtnPin) == True:
                        pass
                    #GPIO.output(Rpin,GPIO.LOW)
                    #GPIO.output(Gpin,GPIO.HIGH)
                    sine(Gpin,GPIO.input(BtnPin))
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        GPIO.cleanup()



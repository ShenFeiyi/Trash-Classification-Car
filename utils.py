#!/usr/bin/python3
# -*- coding:utf-8 -*-
import time
from RPi import GPIO


def biii(frequency, duration):
    buzzer = 17
    freq = frequency
    if not freq == 0:
        interval = 1/freq
        num = 0
        while True:
            if num >= duration*freq:
                break
            num += 1
            GPIO.output(buzzer, GPIO.HIGH)
            time.sleep(interval/2)
            GPIO.output(buzzer, GPIO.LOW)
            time.sleep(interval/2)
    else:
        time.sleep(duration)

def get_freq(note, tone='C'):
    notes = {
        'low1':0,'low1#':1,'low2':2,'low2#':3,'low3':4,'low3#':5,'low4':6,
        'low4#':7,'low5':8,'low5#':9,'low6':10,'low6#':11,'low7':12,
        '1':13,'1#':14,'2':15,'2#':16,'3':17,'3#':18,'4':19,
        '4#':20,'5':21,'5#':22,'6':23,'6#':24,'7':25,
        'high1':26,'high1#':27,'high2':28,'high2#':29,'high3':30,'hig3#':31,'high4':32,
        'high4#':33,'high5':34,'high5#':35,'high6':36,'high6#':37,'high7':38,
        '0':0}
    if tone == 'C':
        std_do = 440 * pow(pow(2,1/12),3)
    elif tone == 'D':
        pass

    if not notes[note] == 0:
        freq = 440 * pow(pow(2,1/12),notes[note]-notes['1'])
    else:
        freq = 0

    return freq

def play_music(music, std_time):
    try:
        if len(music['notes']) == len(music['duration']):
            for i, note in enumerate(music['notes']):
                biii(get_freq(note), std_time*music['duration'][i])
        else:
            print('Check your music.')
    except KeyError:
        print('Check if both "notes" and "duration" exist.')

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17,GPIO.OUT)
    biii(653,1)
    GPIO.cleanup()

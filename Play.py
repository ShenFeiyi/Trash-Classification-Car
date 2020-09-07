#!/usr/bin/python3
# -*- coding:utf-8 -*-

if __name__ == '__main__':
    import time
    from RPi import GPIO

    from utils import play_music
    from Music import Castle_in_the_sky, Canon, Windows, Apple


    buzzer = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzzer, GPIO.OUT)
    
    std_time = 0.2
    play_music(Windows, std_time)
    play_music(Apple, std_time)
    '''
    # Part 1
    std_time = 0.5/2
    #play_music(Canon, std_time)
    play_music(Castle_in_the_sky, std_time)
    '''
    '''
    # Part 2
    from utils import sing

    duration = 0.1
    freq = 0
    while True:
        if freq >= 10000:
            freq += 1000
        elif freq >= 1000:
            freq += 100
        else:
            freq += 10
        biii(freq, duration)
        print(f'Frequency = {freq}Hz')
        if freq > 21000:
            break
    '''
    GPIO.cleanup()


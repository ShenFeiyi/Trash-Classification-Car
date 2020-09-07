#!/usr/bin/python3
# -*- coding:utf-8 -*-
import time
from RPi import GPIO


def _setup():
    
    PWMA = 18
    AIN1 = 22
    AIN2 = 27

    PWMB = 23
    BIN1 = 25
    BIN2 = 24

    GPIO.setwarnings(False) 
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(AIN2,GPIO.OUT)
    GPIO.setup(AIN1,GPIO.OUT)
    GPIO.setup(PWMA,GPIO.OUT)

    GPIO.setup(BIN1,GPIO.OUT)
    GPIO.setup(BIN2,GPIO.OUT)
    GPIO.setup(PWMB,GPIO.OUT)

    L_Motor = GPIO.PWM(PWMA,100)
    L_Motor.start(0)

    R_Motor = GPIO.PWM(PWMB,100)
    R_Motor.start(0)

    return L_Motor, R_Motor

def t_up(speed, t_time, L_Motor, R_Motor, AIN1=22, AIN2=27, BIN1=25, BIN2=24):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,False) #AIN2
    GPIO.output(AIN1,True)  #AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2,False) #BIN2
    GPIO.output(BIN1,True)  #BIN1
    time.sleep(t_time)

def t_stop(t_time, L_Motor, R_Motor, AIN1=22, AIN2=27, BIN1=25, BIN2=24):
    L_Motor.ChangeDutyCycle(0)
    GPIO.output(AIN2,False) #AIN2
    GPIO.output(AIN1,False) #AIN1

    R_Motor.ChangeDutyCycle(0)
    GPIO.output(BIN2,False) #BIN2
    GPIO.output(BIN1,False) #BIN1
    time.sleep(t_time)

def t_down(speed, t_time, L_Motor, R_Motor, AIN1=22, AIN2=27, BIN1=25, BIN2=24):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,True)  #AIN2
    GPIO.output(AIN1,False) #AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2,True)  #BIN2
    GPIO.output(BIN1,False) #BIN1
    time.sleep(t_time)

def t_left(speed, t_time, L_Motor, R_Motor, AIN1=22, AIN2=27, BIN1=25, BIN2=24):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,True)  #AIN2
    GPIO.output(AIN1,False) #AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2,False) #BIN2
    GPIO.output(BIN1,True)  #BIN1
    time.sleep(t_time)

def t_right(speed, t_time, L_Motor, R_Motor, AIN1=22, AIN2=27, BIN1=25, BIN2=24):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,False) #AIN2
    GPIO.output(AIN1,True)  #AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2,True)  #BIN2
    GPIO.output(BIN1,False) #BIN1
    time.sleep(t_time)    


def speed_backward(init_speed, final_speed, accelerate_time, L_Motor, R_Motor, show=False):
    dt = 0.01
    # a = At^2(t-t0)^2
    # v = v0 + A(t^5/5-t0t^4/2+t0^2t^3/3) => A = 30(v-v0)/t0^5
    t0 = accelerate_time
    A = 30*(final_speed-init_speed)/pow(accelerate_time,5)

    if (init_speed==0) and (final_speed==0):
        t_stop(accelerate_time, L_Motor, R_Motor)
    else:
        t = 0
        v = init_speed
        t_up(v,dt,L_Motor,R_Motor)
        while t <= t0:
            if show:
                print('v = {:.2f},\tt = {:.2f},\tt0 = {:.2f}'.format(v,t,t0))
            t += dt
            v += A*(pow(t,4)-2*t0*pow(t,3)+pow(t0,2)*pow(t,2))*dt # v += a*dt
            t_up(v,dt,L_Motor,R_Motor)

def speed_forward(init_speed, final_speed, accelerate_time, L_Motor, R_Motor, show=False):
    dt = 0.01
    # a = At^2(t-t0)^2
    # v = v0 + A(t^5/5-t0t^4/2+t0^2t^3/3) => A = 30(v-v0)/t0^5
    t0 = accelerate_time
    A = 30*(final_speed-init_speed)/pow(accelerate_time,5)

    if (init_speed==0) and (final_speed==0):
        t_stop(accelerate_time, L_Motor, R_Motor)
    else:
        t = 0
        v = init_speed
        t_down(v,dt,L_Motor,R_Motor)
        while t <= t0:
            if show:
                print('v = {:.2f},\tt = {:.2f},\tt0 = {:.2f}'.format(v,t,t0))
            t += dt
            v += A*(pow(t,4)-2*t0*pow(t,3)+pow(t0,2)*pow(t,2))*dt # v += a*dt
            t_down(v,dt,L_Motor,R_Motor)

def turn_right(degree, L_Motor, R_Motor):
    t_time = 2*degree/360
    t_right(50, t_time, L_Motor, R_Motor)
    t_stop(0.1, L_Motor, R_Motor)

def turn_left(degree, L_Motor, R_Motor):
    t_time = 2*degree/360
    t_left(50, t_time, L_Motor, R_Motor)
    t_stop(0.1, L_Motor, R_Motor)

if __name__ == '__main__':
    # Speed Limitation 20 ~ 100
    
    L_Motor, R_Motor = _setup()
    try:
        while True:
            speed_forward(20,80,3,L_Motor,R_Motor,show=True)
            speed_forward(80,20,3,L_Motor,R_Motor,show=True)
            speed_forward(0,0,1,L_Motor,R_Motor)
            speed_backward(20,80,3,L_Motor,R_Motor,show=True)
            speed_backward(80,20,3,L_Motor,R_Motor,show=True)
            speed_backward(0,0,1,L_Motor,R_Motor)
    except KeyboardInterrupt:
        GPIO.cleanup()

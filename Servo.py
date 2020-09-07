#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import serial
from RPi import GPIO

from Adafruit_PWM_Servo_Driver import PWM


def setup_servo():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    info = {}
    
    ser = serial.Serial("/dev/ttyAMA0",9600)  #串口波特率设置
    pwm = PWM(0x40, debug=False)
    info['ser'] = ser
    info['pwm'] = pwm

    servoMin = 150  # Min pulse length out of 4096
    servoMax = 600  # Max pulse length out of 4096
    info['servoMin'] = servoMin
    info['servoMax'] = servoMax
    
    #SERVO
    myservo1 = 0
    info['myservo1'] = {}
    info['myservo1']['id'] = myservo1
    myservo2 = 1
    info['myservo2'] = {}
    info['myservo2']['id'] = myservo2
    myservo3 = 2
    info['myservo3'] = {}
    info['myservo3']['id'] = myservo3
    myservo4 = 3
    info['myservo4'] = {}
    info['myservo4']['id'] = myservo4

    SERVOS = 4  #舵机数4个

    #定义舵机的角度值初始化
    #手爪
    ms1MIN = 10
    ms1MAX = 50
    ms1INITANGLE = 28
    ms1currentAngle = 0
    info['myservo1']['min'] = ms1MIN
    info['myservo1']['max'] = ms1MAX
    info['myservo1']['init'] = ms1INITANGLE
    info['myservo1']['current'] = ms1currentAngle

    #上臂电机
    ms2MIN = 10
    ms2MAX = 140
    ms2INITANGLE = 70
    ms2currentAngle = 0
    info['myservo2']['min'] = ms2MIN
    info['myservo2']['max'] = ms2MAX
    info['myservo2']['init'] = ms2INITANGLE
    info['myservo2']['current'] = ms2currentAngle

    #下臂电机
    ms3MIN = 40
    ms3MAX = 170
    ms3INITANGLE = 120
    ms3currentAngle = 0
    info['myservo3']['min'] = ms3MIN
    info['myservo3']['max'] = ms3MAX
    info['myservo3']['init'] = ms3INITANGLE
    info['myservo3']['current'] = ms3currentAngle

    #底座
    ms4MIN = 0
    ms4MAX = 170
    ms4INITANGLE = 25
    ms4currentAngle = 0
    info['myservo4']['min'] = ms4MIN
    info['myservo4']['max'] = ms4MAX
    info['myservo4']['init'] = ms4INITANGLE
    info['myservo4']['current'] = ms4currentAngle

    ServoDelayTime = 0.05 #舵机响应时间
    delta = 0.1        #舵机转动幅度
    info['ServoDelayTime'] = ServoDelayTime
    info['delta'] = delta

    pwm.setPWMFreq(50)

    return info

def setServoPulse(channel, pulse, pwm):
    pulseLength = 1e6
    pulseLength /= 50.0
    #print("%d us per period" % pulseLength)
    pulseLength /= 4096.0
    #print("%d us per bit" % pulseLength)
    pulse *= 1e3
    pulse /= (pulseLength*1.0)
    #print("pluse: %f  " % (pulse))
    pwm.setPWM(channel, 0, int(pulse))

#Angle to PWM
def write(servonum,x,pwm):
    y = x/90.0+0.5
    y = max(y,0.5)
    y = min(y,2.5)
    setServoPulse(servonum,y,pwm)

def ServoInit(info):
    ms1currentAngle = info['myservo1']['current']
    ms2currentAngle = info['myservo2']['current']
    ms3currentAngle = info['myservo3']['current']
    ms4currentAngle = info['myservo4']['current']

    myservo1 = info['myservo1']['id']
    myservo2 = info['myservo2']['id']
    myservo3 = info['myservo3']['id']
    myservo4 = info['myservo4']['id']

    ms1INITANGLE = info['myservo1']['init']
    ms2INITANGLE = info['myservo2']['init']
    ms3INITANGLE = info['myservo3']['init']
    ms4INITANGLE = info['myservo4']['init']
    
    write(myservo1,ms1INITANGLE,info['pwm'])   #手爪  
    write(myservo2,ms2INITANGLE,info['pwm'])   #上臂  
    write(myservo3,ms3INITANGLE,info['pwm'])   #下臂  
    write(myservo4,ms4INITANGLE,info['pwm'])   #底座
  
    ms1currentAngle = ms1INITANGLE
    ms2currentAngle = ms2INITANGLE
    ms3currentAngle = ms3INITANGLE
    ms4currentAngle = ms4INITANGLE

    info['myservo1']['current'] = ms1currentAngle
    info['myservo2']['current'] = ms2currentAngle
    info['myservo3']['current'] = ms3currentAngle
    info['myservo4']['current'] = ms4currentAngle
    
    time.sleep(1)

    return info

#-------------------机械臂运动函数定义----------------
def ClampOpen(info):  #手爪打开
    myservo1 = info['myservo1']['id']
    ms1MAX = info['myservo1']['max']
    write(myservo1,ms1MAX,info['pwm'])
    time.sleep(0.3)
    return info

def ClampClose(info): #手臂闭合
    myservo1 = info['myservo1']['id']
    ms1MIN = info['myservo1']['min']
    write(myservo1,ms1MIN,info['pwm'])
    time.sleep(0.3)
    return info

def BottomLeft(info): #底座左转
    myservo4 = info['myservo4']['id']
    ms4MAX = info['myservo4']['max']
    ms4currentAngle = info['myservo4']['current']
    delta = info['delta']
    if(ms4currentAngle + delta) < ms4MAX:
        ms4currentAngle += delta
    write(myservo4,ms4currentAngle,info['pwm'])
    info['myservo4']['current'] = ms4currentAngle
    return info

def BottomRight(info): #底座右转
    myservo4 = info['myservo4']['id']
    ms4MIN = info['myservo4']['min']
    ms4currentAngle = info['myservo4']['current']
    delta = info['delta']
    if(ms4currentAngle - delta) > ms4MIN:
        ms4currentAngle -= delta
    write(myservo4,ms4currentAngle,info['pwm'])
    info['myservo4']['current'] = ms4currentAngle
    return info

def Arm_A_Up(info): #上臂舵机向上
    myservo2 = info['myservo2']['id']
    ms2MAX = info['myservo2']['max']
    ms2currentAngle = info['myservo2']['current']
    delta = info['delta']
    if(ms2currentAngle + delta) < ms2MAX:
        ms2currentAngle += delta
    write(myservo2,ms2currentAngle,info['pwm'])
    info['myservo2']['current'] = ms2currentAngle
    return info

def Arm_A_Down(info):#上臂舵机向下
    myservo2 = info['myservo2']['id']
    ms2MIN = info['myservo2']['min']
    ms2currentAngle = info['myservo2']['current']
    delta = info['delta']
    if(ms2currentAngle - delta) > ms2MIN:
        ms2currentAngle -= delta
    write(myservo2,ms2currentAngle,info['pwm'])
    info['myservo2']['current'] = ms2currentAngle
    return info
  
def Arm_B_Up(info):#下臂舵机向上
    myservo3 = info['myservo3']['id']
    ms3MIN = info['myservo3']['min']
    ms3currentAngle = info['myservo3']['current']
    delta = info['delta']
    if(ms3currentAngle - delta) > ms3MIN:
        ms3currentAngle -= delta
    write(myservo3,ms3currentAngle,info['pwm'])
    info['myservo3']['current'] = ms3currentAngle
    return info

def Arm_B_Down(info): #下臂舵机向下
    myservo3 = info['myservo3']['id']
    ms3MAX = info['myservo3']['max']
    ms3currentAngle = info['myservo3']['current']
    delta = info['delta']
    if(ms3currentAngle + delta) < ms3MAX:
        ms3currentAngle += delta
    write(myservo3,ms3currentAngle,info['pwm'])
    info['myservo3']['current'] = ms3currentAngle
    return info

def Servo_stop(info): #停止所有舵机
    myservo1 = info['myservo1']['id']
    myservo2 = info['myservo2']['id']
    myservo3 = info['myservo3']['id']
    myservo4 = info['myservo4']['id']
    ms1currentAngle = info['myservo1']['current']
    ms2currentAngle = info['myservo2']['current']
    ms3currentAngle = info['myservo3']['current']
    ms4currentAngle = info['myservo4']['current']
    write(myservo1,ms1currentAngle,info['pwm'])
    write(myservo2,ms2currentAngle,info['pwm'])
    write(myservo3,ms3currentAngle,info['pwm']) 
    write(myservo4,ms4currentAngle,info['pwm'])
    return info

def UP(info):
    for _ in range(500):
        info = Arm_B_Up(info)
    for _ in range(850):
        info = BottomRight(info)
    return info

def DOWN(info):
    for _ in range(850):
        info = BottomLeft(info)
    for _ in range(500):
        info = Arm_B_Down(info)
    return info

#/-------------------机械臂运动函数定义----------------

if __name__ == '__main__':
    info = setup_servo()
    ser = info['ser']
    info = ServoInit(info) # 收起
    for i in range(2):
        # 放下
        for _ in range(850):
            info = BottomLeft(info)
        for _ in range(500):
            info = Arm_B_Down(info)

        time.sleep(3)

        # 收起
        for _ in range(500):
            info = Arm_B_Up(info)
        for _ in range(850):
            info = BottomRight(info)
    '''
    while True:
        try:
            for _ in range(500):
                info = BottomLeft(info)
            for _ in range(500):
                info = BottomRight(info)
            for _ in range(500):
                info = Arm_A_Up(info)
            for _ in range(500):
                info = Arm_B_Up(info)
            for _ in range(500):
                info = Arm_B_Down(info)
            for _ in range(500):
                info = Arm_A_Down(info)
            for _ in range(500):
                info = Arm_B_Up(info)
            for _ in range(500):
                info = Arm_B_Down(info)
        except KeyboardInterrupt:
            info = Servo_stop(info)
            GPIO.cleanup()
            break
    '''

    for item in info:
        print(f'{item}:{info[item]}')

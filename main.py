#!/usr/bin/python3
# -*- coding:utf-8 -*-
import os
import time
import picamera
import numpy as np
from RPi import GPIO
from PIL import Image

from Ultrasonics import biu
from utils import biii, play_music
from yolo_cmdline import yolo_detect
from Music import Windows, Castle_in_the_sky
from Servo import UP, DOWN, setup_servo, ServoInit
from BasicMovement import speed_forward, speed_backward, turn_right, turn_left


def setup():
    print('GPIO...',end='')
    GPIO.setwarnings(False) 
    GPIO.setmode(GPIO.BCM)
    print('...正常')

    info = {}

    # Movement
    print('动力系统...',end='')
    PWMA = 18
    AIN1 = 22
    AIN2 = 27

    PWMB = 23
    BIN1 = 25
    BIN2 = 24

    GPIO.setup(AIN2,GPIO.OUT)
    GPIO.setup(AIN1,GPIO.OUT)
    GPIO.setup(PWMA,GPIO.OUT)

    GPIO.setup(BIN1,GPIO.OUT)
    GPIO.setup(BIN2,GPIO.OUT)
    GPIO.setup(PWMB,GPIO.OUT)

    L_Motor = GPIO.PWM(PWMA,100)
    L_Motor.start(0)
    info['L_Motor'] = L_Motor

    R_Motor = GPIO.PWM(PWMB,100)
    R_Motor.start(0)
    info['R_Motor'] = R_Motor
    print('...正常')

    # Button
    print('按键...',end='')
    BtnPin = 19
    Gpin = 5
    Rpin = 6

    GPIO.setup(Gpin, GPIO.OUT)
    GPIO.setup(Rpin, GPIO.OUT)
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print('...正常')

    # Buzzer
    print('蜂鸣器...',end='')
    buzzer = 17
    GPIO.setup(buzzer, GPIO.OUT)

    for _ in range(3):
        biii(653,0.1)
        time.sleep(0.1)
    print('...正常')

    # Ultrasonics
    print('超声波系统...',end='')
    ECHO = 19
    TRIG = 17

    GPIO.setup(ECHO, GPIO.IN)
    GPIO.setup(TRIG, GPIO.OUT)

    for _ in range(10):
        d = biu()
        time.sleep(0.1)
    print('...正常')

    # Arm
    print('机械臂...',end='')
    servo_info = setup_servo()
    servo_info = ServoInit(servo_info)
    info['servo'] = servo_info
    print('...正常')

    print('权重文件...',end='')
    weights_path = os.path.join('/','home','pi','darknet-nnpack','weights')
    weights = []
    weights.append(os.path.join('/','home','pi','darknet-nnpack','weights','yolov3-tiny_080000.weights'))
    weights.append(os.path.join('/','home','pi','darknet-nnpack','weights','yolov3-tiny_060000.weights'))
    weights.append(os.path.join('/','home','pi','darknet-nnpack','weights','yolov3-tiny_100000.weights'))
    weights.append(os.path.join('/','home','pi','darknet-nnpack','weights','yolov3-tiny_482000.weights'))
    weights_names = os.listdir(weights_path)
    weights_names = [os.path.join('/','home','pi','darknet-nnpack','weights',name) for name in weights_names if name.endswith('weights')]
    weights_names.sort()
    for name in weights_names:
        if not name in weights:
            weights.append(name)
    info['weights'] = weights
    print('...就绪')

    return info

def ScanKey():
    BtnPin = 19
    Gpin = 5
    Rpin = 6
    
    val = GPIO.input(BtnPin)
    while GPIO.input(BtnPin) == False:
        val = GPIO.input(BtnPin)
    while GPIO.input(BtnPin) == True:
        time.sleep(0.01)
        val = GPIO.input(BtnPin)
        if val == True:
            GPIO.output(Rpin,1)
            while GPIO.input(BtnPin) == False:
                GPIO.output(Rpin,0)
        else:
            GPIO.output(Rpin,0)

if __name__ == '__main__':
    try:
        info = setup()
        print('树莓派小车启动')
        #play_music(Windows, 0.17)
        print('按下 ctrl+c 紧急退出')
        print('按键以继续')
        #ScanKey()

        confidence = None
        while_count = 0
        while not confidence:
            if not while_count == 0:
                random_degree = 360*np.random.rand() - 180
                if random_degree >=0:
                    turn_right(random_degree,info['L_Motor'],info['R_Motor'])
                else:
                    turn_left(random_degree,info['L_Motor'],info['R_Motor'])
            
            # Take a picture
            ## -*- Overview -*- ##
            camera = picamera.PiCamera()
            biii(653,0.1)
            time.sleep(0.1)
            camera.capture('you_only_look_once.jpg')
            camera.close()
            img = Image.open('you_only_look_once.jpg')
            img = img.rotate(90,expand=True)
            img = img.crop((0.15*img.size[0],0.35*img.size[1],0.85*img.size[0],0.75*img.size[1]))
            img.save('you_only_look_once.jpg')

            weights_count = 0
            while weights_count < len(info['weights']):
                # Yolov3-tiny
                params = {}
                params['image'] = 'you_only_look_once.jpg'
                params['names'] = '/home/pi/darknet-nnpack/data/trash25.names'
                params['config'] = '/home/pi/darknet-nnpack/cfg/yolov3-trash25.cfg'
                params['weights'] = info['weights'][weights_count]
                weights_count += 1

                start = time.time()
                label, confidence, x, y = yolo_detect(params)
                finish = time.time()
                if (type(label)==str) and (type(confidence)==float):
                    print('yolo检测共 {:.2f} 秒'.format(finish - start))
                    print('种类:{:s}\t置信度:{:.2f}%\t({:.1f},{:.1f})'.format(label,100*confidence,x,y))
                if confidence:
                    break
            # end of `while weights_count < len(info['weights'])`

            while_count += 1
            if while_count == 10:
                print('附近没有找到垃圾')
                break
        # end of `while not confidence`

        if (not while_count == 10) and (not confidence == None):
            # Aim at target
            img = Image.open('you_only_look_once.jpg')
            xlength = img.size[0]
            theta = np.arctan((x-xlength/2)/(10*xlength/9))*180/np.pi
            if theta >= 0:
                turn_right(theta,info['L_Motor'],info['R_Motor'])
            else:
                theta = -theta
                turn_left(theta,info['L_Motor'],info['R_Motor'])

            # Go forward
            distance = biu()
            print('{:.2f} mm'.format(distance))
            init_speed = 20
            final_speed = 50
            speed_forward(init_speed,final_speed,0.1,info['L_Motor'],info['R_Motor'])
            while distance > 500:
                distance = biu()
                print('{:.2f} mm'.format(distance))
                time.sleep(0.1)
                speed_forward(50,50,0.1,info['L_Motor'],info['R_Motor'])
            init_speed = 50
            final_speed = 20
            speed_forward(init_speed,final_speed,0.1,info['L_Motor'],info['R_Motor'])
            speed_forward(0,0,1,info['L_Motor'],info['R_Motor'])

            # Take a picture
            ## -*- Review -*- ##
            camera = picamera.PiCamera()
            biii(653,0.1)
            time.sleep(0.1)
            camera.capture('you_only_look_once.jpg')
            camera.close()
            img = Image.open('you_only_look_once.jpg')
            img = img.rotate(90,expand=True)
            img = img.crop((0,0.2*img.size[1],img.size[0],img.size[1]))
            img.save('you_only_look_once.jpg')

            weights_count = 0
            while weights_count < len(info['weights']):
                # Yolov3-tiny
                params = {}
                params['image'] = 'you_only_look_once.jpg'
                params['names'] = '/home/pi/darknet-nnpack/data/trash25.names'
                params['config'] = '/home/pi/darknet-nnpack/cfg/yolov3-trash25.cfg'
                params['weights'] = info['weights'][weights_count]
                weights_count += 1

                start = time.time()
                label, confidence, x, y = yolo_detect(params)
                finish = time.time()
                if (type(label)==str) and (type(confidence)==float):
                    print('yolo检测共 {:.2f} 秒'.format(finish - start))
                    print('种类:{:s}\t置信度:{:.2f}%\t({:.1f},{:.1f})'.format(label,100*confidence,x,y))
                if confidence:
                    break
            # end of `while weights_count < len(info['weights'])`

            # Aim at target
            img = Image.open('you_only_look_once.jpg')
            xlength = img.size[0]
            theta = np.arctan((x-xlength/2)/(10*xlength/9))*180/np.pi
            if theta >= 0:
                turn_right(theta,info['L_Motor'],info['R_Motor'])
            else:
                theta = -theta
                turn_left(theta,info['L_Motor'],info['R_Motor'])

            # Go forward
            distance = biu()
            print('{:.2f} mm'.format(distance))
            init_speed = 20
            final_speed = 30
            speed_forward(init_speed,final_speed,0.1,info['L_Motor'],info['R_Motor'])
            while distance > 80:
                distance = biu()
                print('{:.2f} mm'.format(distance))
                time.sleep(0.1)
                speed_forward(30,30,0.1,info['L_Motor'],info['R_Motor'])
            init_speed = 30
            final_speed = 20
            speed_forward(init_speed,final_speed,0.1,info['L_Motor'],info['R_Motor'])
            speed_forward(0,0,1,info['L_Motor'],info['R_Motor'])

            # Arm
            info['servo'] = DOWN(info['servo'])
            time.sleep(1)
            speed_backward(20,50,1,info['L_Motor'],info['R_Motor'])
            speed_backward(50,20,1,info['L_Motor'],info['R_Motor'])
            speed_backward(0,0,1,info['L_Motor'],info['R_Motor'])
            time.sleep(1)
            info['servo'] = UP(info['servo'])
            _ = setup_servo() # 机械臂松弛
        # end of `if (not while_count == 10) and (not confidence == None)`
            
    except KeyboardInterrupt:
        print('紧急退出')
        speed_forward(0,0,1,info['L_Motor'],info['R_Motor'])
    finally:
        #play_music(Castle_in_the_sky, 0.3)
        _ = setup_servo() # 机械臂松弛
        speed_backward(20,20,8,info['L_Motor'],info['R_Motor'])
        speed_backward(0,0,1,info['L_Motor'],info['R_Motor'])
        print('\n -*- END -*- \n')

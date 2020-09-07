#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time

from yolo_cmdline import yolo_detect


imgpath = os.path.join('.','images')
weightspath = os.path.join('/','home','pi','darknet-nnpack','weights')

imagenames = os.listdir(imgpath)
weightnames = os.listdir(weightspath)

imagenames = [os.path.join(imgpath,name) for name in imagenames if name.endswith('jpg')]
weightnames = [os.path.join(weightspath,name) for name in weightnames if name.endswith('weights')]
imagenames.sort()
weightnames.sort()

with open('weights.txt','w') as file:
    for imgname in imagenames:
        file.write(imgname+'\n')
        for weights in weightnames:
            file.write('\t'+weights+'\t')
            params = {}
            params['image'] = imgname
            params['weights'] = weights
            label, confidence, x, y = yolo_detect(params)
            file.write(str(label)+' '+str(confidence)+' '+str(x)+' '+str(y)+'\n')

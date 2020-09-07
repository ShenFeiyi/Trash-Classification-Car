#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
import argparse
import cv2 as cv
import numpy as np


def yolo_detect(params):

    '''
    pathIn：原始图片的路径
    label_path：类别标签文件的路径
    config_path：模型配置文件的路径
    weights_path：模型权重文件的路径
    confidence_thre：0-1，置信度（概率/打分）阈值，即保留概率大于这个值的边界框，默认为0.5
    nms_thre：非极大值抑制的阈值，默认为0.3
    '''
    if 'image' in params:
        pathIn = params['image']
    else:
        pathIn = ''
    if 'names' in params:
        label_path = params['names']
    else:
        label_path = '/home/pi/darknet-nnpack/data/trash25.names'
    if 'config' in params:
        config_path = params['config']
    else:
        config_path = '/home/pi/darknet-nnpack/cfg/yolov3-trash25.cfg'
    if 'weights' in params:
        weights_path = params['weights']
    else:
        weights_path = '/home/pi/darknet-nnpack/yolov3-482.weights'
    if 'confidence' in params:
        confidence_thre = params['confidence']
    else:
        confidence_thre = 0.1
    if 'num' in params:
        nms_thre = params['num']
    else:
        nms_thre = 0.3

    # 加载类别标签文件
    LABELS = open(label_path).read().strip().split("\n")
    nclass = len(LABELS)

    # 为每个类别的边界框随机匹配相应颜色
    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(nclass, 3), dtype='uint8')

    # 载入图片并获取其维度
    base_path = os.path.basename(pathIn)
    img = cv.imread(pathIn)
    (H, W) = img.shape[:2]

    # 加载模型配置和权重文件
    net = cv.dnn.readNetFromDarknet(config_path, weights_path)

    # 获取YOLO输出层的名字
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    # 将图片构建成一个blob，设置图片尺寸，然后执行一次YOLO前馈网络计算，最终获取边界框和相应概率
    blob = cv.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    # 初始化边界框，置信度（概率）以及类别
    boxes = []
    confidences = []
    classIDs = []

    # 迭代每个输出层，总共三个
    for output in layerOutputs:
        # 迭代每个检测
        for detection in output:
            # 提取类别ID和置信度
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            
            # 只保留置信度大于某值的边界框
            if confidence > confidence_thre:
                # 将边界框的坐标还原至与原图片相匹配，记住YOLO返回的是边界框的中心坐标以及边界框的宽度和高度
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                # 更新边界框，置信度（概率）以及类别
                boxes.append([int(centerX), int(centerY), int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    # 使用非极大值抑制方法抑制弱、重叠边界框
    idxs = cv.dnn.NMSBoxes(boxes, confidences, confidence_thre, nms_thre)

    # 确保至少一个边界框
    if len(idxs) > 0:
        (centerx,centery) = (boxes[0][0], boxes[0][1])
        # 迭代每个边界框
        imax = 0
        confidencesmax = confidences[0]
        for i in idxs.flatten():
            if confidences[i] > confidencesmax:
                imax = i
                confidencesmax = confidences[i]
                # 提取边界框的坐标
                (centerx,centery) = (boxes[i][0], boxes[i][1])
        return LABELS[classIDs[imax]], confidences[imax], centerx, centery
    else:
        return None, None, None, None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--weights', type=str, default='/home/pi/darknet-nnpack/yolov3-482.weights', help='.weights file')
    parser.add_argument('-c', '--config', type=str, default='/home/pi/darknet-nnpack/cfg/yolov3-trash25.cfg', help='.cfg file')
    parser.add_argument('-n', '--names', type=str, default='/home/pi/darknet-nnpack/data/trash25.names', help='.names file')
    parser.add_argument('--image', type=str, default='/home/pi/darknet-nnpack/data/items.jpg', help='image file')
    parser.add_argument('--confidence', type=float, default=0.5, help='confidence threshold')
    parser.add_argument('--num', type=float, default=0.3, help='num threshold')
    parser.add_argument('--jpg', type=int, default=80, help='JPEG image quality')
    args = parser.parse_args()
    params = vars(args)

    start = time.time()
    label, confidence, x, y = yolo_detect(params)
    end = time.time()
    print('加载YOLO模型检测共花费 {:.2f} 秒'.format(end - start))
    print('目标类别：{}'.format(label))
    print('置信度：{:.3f}'.format(confidence))
    print('目标中心位置：{:.1f},{:.1f}'.format(x, y))

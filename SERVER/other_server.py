import json
import torch
import os
import socket
import cv2
import numpy
import base64
import glob
import sys
import time
import threading
from datetime import datetime
from ultralytics import YOLO
from cyclegan_turbo import CycleGAN_Turbo

#Load CycleGAN to memory
cyclegan_model = CycleGAN_Turbo(pretrained_name="night_to_day")
cyclegan_model.eval()  # 평가 모드 설정
cyclegan_model.unet.enable_xformers_memory_efficient_attention()

model = YOLO('./best.pt')

clients = []

SERVER_IP = '175.45.194.40'
SERVER_PORT = 8080

class Socket:

    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.sock = None
        self.socketOpen()

    def socketClose(self):
        self.sock.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is close')

    def socketOpen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is open')

def is_low_light(image, threshold=50):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = gray.mean()
    return mean_brightness < threshold
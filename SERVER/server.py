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

# CycleGAN 및 YOLO 모델 로드
cyclegan_model = CycleGAN_Turbo(pretrained_name="night_to_day")
cyclegan_model.eval()
cyclegan_model.unet.enable_xformers_memory_efficient_attention()

model = YOLO('./best.pt')

# 클라이언트 연결을 위한 큐
client_queue = queue.Queue()

SERVER_IP = '175.45.194.40'
SERVER_PORT = 8080
TIMEOUT = 10  # 소켓 타임아웃 설정 (10초)

# 소켓 클래스
class Socket:
    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.sock = None
        self.socketOpen()

    def socketClose(self):
        self.sock.close()
        print(f'Server socket [ TCP_IP: {self.TCP_IP}, TCP_PORT: {self.TCP_PORT} ] is closed')

    def socketOpen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen()
        self.sock.settimeout(TIMEOUT)  # 타임아웃 설정
        print(f'Server socket [ TCP_IP: {self.TCP_IP}, TCP_PORT: {self.TCP_PORT} ] is open')

# 이미지 밝기 확인 함수
def is_low_light(image, threshold=50):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = gray.mean()
    return mean_brightness < threshold

# YOLO 모델 예측 및 클래스별 JSON 데이터 생성
def generate_class_value(cls):
    if cls == 0:
        return {"r": 255, "g": 255, "b": 0, "lx": 50, "cls": "Eating person"}
    elif cls == 2:
        return {"r": 204, "g": 0, "b": 0, "lx": 50, "cls": "Sleeping person"}
    elif cls == 3:
        return {"r": 51, "g": 0, "b": 255, "lx": 50, "cls": "Studying person"}
    return None

# CycleGAN 변환 함수
transform = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])
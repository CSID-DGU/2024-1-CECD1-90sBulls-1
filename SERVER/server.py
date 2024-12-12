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
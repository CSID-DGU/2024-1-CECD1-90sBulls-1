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
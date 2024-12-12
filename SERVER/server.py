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
